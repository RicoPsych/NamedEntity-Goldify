import random
import requests
import tqdm
from time import sleep
from models.Dataset import Dataset
from models.Document import Document
from models.Entity import Entity
from math import log 
from Utilities import get_proxy_list

def rq_url(search_term): 
    return f"http://en.wikipedia.org/w/api.php?action=query&format=json&prop=&list=search&formatversion=2&srsearch={search_term}&srlimit=1&srinfo=totalhits"

def get_hits(search_term,proxy_dict = None):
    #sleep(0.05) since requests are done sequentially, the sleep is not needed
    rq = requests.get(rq_url(search_term),proxies=proxy_dict)
    try:
        return rq.json()["query"]["searchinfo"]["totalhits"]
    except KeyError:
        print(f"(Coherence) No results in search for '{search_term}', returning 0")
        return 0
    
#normalized wiki distance
#for each NWD - max 3 requests
def NWD(term1, term2, cached_requests = {}, proxy_dict = None):
    N = 6942644000 #get_hits("the")
    x = cached_requests[term1] = cached_requests.get(term1, get_hits(term1, proxy_dict))
    y = cached_requests[term2] = cached_requests.get(term2, get_hits(term2, proxy_dict))
    xy = cached_requests[f"{term1} {term2}"] =  cached_requests[f"{term2} {term1}"] = cached_requests.get(f"{term1} {term2}", get_hits(f"{term1} {term2}", proxy_dict)) 
    
    if x == 0 or y == 0 or xy == 0:
        return 1 #float("inf")

    log_N = log(N,2)
    log_x = log(x,2)
    log_y = log(y,2)
    log_xy = log(xy,2)
    return ( max(log_x,log_y) - log_xy) / (log_N - min(log_x, log_y))


def EntityCoherence(dataset):
    if isinstance(dataset,Dataset):
        documents = dataset.documents
    elif isinstance(dataset,list) and isinstance(dataset[0],Document):
        documents = dataset
    elif isinstance(dataset,Document):
        documents = [dataset]
    else:
        raise "Invalid Input dataset"
    
    # Number of results for "the", proxy for total pages
    #N = get_hits("the")# 6942644000
    cached_requests = {}
    proxies_list = get_proxy_list()

    dataset_NWD_micro = 0 #all entities
    dataset_NWD_macro = 0 #averaged over documents
    entities_count = 0
    documentsNWD = {}

    print("Entity Coherence:")
    for document in tqdm.tqdm(documents,desc="Documents"):
        entities_count += len(document.entities)

        doc_sum_nwd = 0
        for i in tqdm.tqdm(range(len(document.entities)),desc="Entities"):
            e = document.entities[i].kb_name
            eb = document.entities[i-1 if i - 1 >= 0 else i + 1].kb_name
            ef = document.entities[i+1 if i + 1 < len(document.entities) else i - 1].kb_name
            #proxy_dict = random.choice(proxies_list)
            #for each entity 2x NWD -> 6x requests for each entitiy 
            neighbourNWD = (NWD(e,eb,cached_requests) + NWD(e,ef,cached_requests)) / 2
            doc_sum_nwd += neighbourNWD
            #print(neighbourNWD) 
        doc_nwd = doc_sum_nwd/len(document.entities)

        dataset_NWD_micro += doc_sum_nwd #entities sum
        dataset_NWD_macro += doc_nwd #document nwd
        documentsNWD[document.name] = doc_nwd
        #document.name
    print("Done")

    dataset_NWD_micro /= entities_count
    dataset_NWD_macro /= len(documents)
    # print(f"micro:{dataset_NWD_micro}, macro:{dataset_NWD_macro}")
    return {
        "micro_NWD": dataset_NWD_micro,
        "macro_NWD": dataset_NWD_macro,
        "per_document_NWD": documentsNWD
    }
 

