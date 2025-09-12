from pathlib import Path
from typing import Literal
import requests
import tqdm
from time import sleep
import sqlite3

import urllib
from models.Dataset import Dataset
from models.Document import Document
from models.Entity import Entity
from math import log 
from Utilities import get_proxy_list
from Utilities import Singleton


class UserAgent(metaclass=Singleton):
    def __init__(self, user_agent):
        self.user_agent_str = user_agent

class RequestsCache(metaclass=Singleton):
    def __init__(self, path = "./data/wiki_cached_requests.db"):
        self.connection = sqlite3.connect(path)
        self.cursor = self.connection.cursor()
        if self.cursor.execute("SELECT name FROM sqlite_master WHERE name='entity'").fetchone() is None:
            self.cursor.execute("CREATE TABLE entity(searchterm, hits)")

    def select(self, key:str) -> None | int :
        response = self.cursor.execute("SELECT searchterm,hits FROM entity WHERE searchterm = ?", [key]).fetchone()
        value = response[1] if response is not None else None
        return value

    def insert(self, key:str, value:int) -> int:
        self.cursor.execute("INSERT INTO entity VALUES ( ? , ? )", [key, value])
        self.connection.commit()
        return value

    def __getitem__(self, key):
        return self.select(key)

    def __setitem__(self, key, value):
        return self.insert(key,value)
    
    def get(self, key, default = None):
        value = self.select(key) 
        return value if value is not None else default

# def load_cached_requests(path = "./data/wiki_cached_requests.json"):
#     cache_path = Path(path)
#     if not cache_path.exists():
#         cache = {}
#     else:
#         with open(path,"r+") as file: 
#             print(f"Loading coherence cache:{path}")
#             cache = json.load(file)
#     return cache

# def save_cached_requests(cache, path = "./data/wiki_cached_requests.json"):
#     path = Path(path)
#     if path.exists(): #keep previous cache, 
#         os.replace(path,path.replace(path.stem, path.stem + "_prev"))
#     try:
#         with open(path, "w+") as file:
#             json.dump(cache, file)
#     except:
#         if path.exists(): #if error occurrs during write, revert the previous file as cache
#             os.replace(path.replace(path.stem, path.stem + "_prev"),path)


def rq_url(search_term, lang:Literal["en","fr","es","de"] ="en"): 
    return f"http://{lang}.wikipedia.org/w/api.php?action=query&format=json&prop=&list=search&formatversion=2&srsearch={urllib.parse.quote_plus(search_term)}&srlimit=1&srinfo=totalhits"

def get_hits(search_term,proxy_dict = None, lang:Literal["en","fr","es","de"] ="en"):
    headers = {'User-Agent': UserAgent().user_agent_str}
    #sleep(0.05) since requests are done sequentially, the sleep is not needed
    rq = requests.get(rq_url(search_term,lang),headers=headers,proxies=proxy_dict)
    try:
        return rq.json()["query"]["searchinfo"]["totalhits"]
    except KeyError:
        tqdm.tqdm.write(f"(Coherence) No results in search for '{search_term}', returning 0")
        return 0
    
#normalized wiki distance
#for each NWD - max 3 requests
def NWD(term1, term2, cached_requests = {}, proxy_dict = None, lang:Literal["en","fr","es","de"] ="en"):
    term1 = term1.lower() 
    term2 = term2.lower()
    term1_2 = f"{term1} {term2}"
    term2_1 = f"{term2} {term1}"
    N = 6942644000 #get_hits("the")    # Number of results for "the", proxy for total pages
    
    x = cached_requests.get(term1)
    if x is None:
        x = cached_requests[term1] = get_hits(term1, proxy_dict, lang)
    y = cached_requests.get(term2)
    if y is None:
        y = cached_requests[term2] = get_hits(term2, proxy_dict, lang)
    xy = cached_requests.get(term1_2) or cached_requests.get(term2_1)
    if xy is None: 
        xy = cached_requests[term1_2] = cached_requests[term2_1] = get_hits(term1_2, proxy_dict, lang) 
    
    if x == 0 or y == 0 or xy == 0:
        return 1 #float("inf")

    log_N = log(N,2)
    log_x = log(x,2)
    log_y = log(y,2)
    log_xy = log(xy,2)
    return ( max(log_x,log_y) - log_xy) / (log_N - min(log_x, log_y))


def EntityCoherence(dataset, user_agent = None, use_common_cache = True, lang:Literal["en","fr","es","de"] ="en"):
    if isinstance(dataset,Dataset):
        documents = dataset.documents
    elif isinstance(dataset,list) and isinstance(dataset[0],Document):
        documents = dataset
    elif isinstance(dataset,Document):
        documents = [dataset]
    else:
        raise "Invalid Input dataset"
    
    UserAgent(user_agent = user_agent)

    if lang != "en" and use_common_cache:
        #Cache stores the hit results for search terms, does not recognize different languages, on different wikipedia language versions the hit amount will differ.
        tqdm.tqdm.write("Coherence Warning: Remember to replace or remove cache file, when using different languages.")


    cached_requests = RequestsCache() if use_common_cache else {}

    dataset_NWD_micro = 0 #all entities
    dataset_NWD_macro = 0 #averaged over documents
    entities_count = 0
    documentsNWD = {}

    tqdm.tqdm.write("Entity Coherence:")
    skipped_documents = 0
    for document in tqdm.tqdm(documents, desc="Documents"):
        entities_count += len(document.entities)

        doc_sum_nwd = 0
        if len(document.entities) > 1 : #Skipping documents when not enough entities
            for i in tqdm.tqdm(range(len(document.entities)),desc="Entities"):
                prev_i = i-1 if i - 1 >= 0 else i + 1
                next_i = i+1 if i + 1 < len(document.entities) else i - 1
                
                e = document.entities[i].kb_name or document.entities[i].surface_form 
                eb = document.entities[prev_i].kb_name or document.entities[prev_i].surface_form
                ef = document.entities[next_i].kb_name or document.entities[next_i].surface_form
                #proxy_dict = random.choice(proxies_list)
                #for each entity 2x NWD -> 6x requests for each entitiy 
                neighbourNWD = (NWD(e,eb,cached_requests,lang=lang) + NWD(e,ef,cached_requests,lang=lang)) / 2
                doc_sum_nwd += neighbourNWD
                #print(neighbourNWD) 
            doc_nwd = doc_sum_nwd/len(document.entities)

            dataset_NWD_micro += doc_sum_nwd #entities sum
            dataset_NWD_macro += doc_nwd #document nwd
            documentsNWD[document.name] = doc_nwd
     
    tqdm.tqdm.write("Done")

    dataset_NWD_micro /= entities_count
    dataset_NWD_macro /= (len(documents) - skipped_documents)
    return {
        "micro_NWD": dataset_NWD_micro,
        "macro_NWD": dataset_NWD_macro,
        "excluded_documents": skipped_documents,
        "per_document_NWD": documentsNWD
    }
 

