from time import sleep
from models.Dataset import Dataset
from models.Document import Document
from models.Entity import Entity
import requests
from math import log 

def rq_url(search_term): 
    return f"https://en.wikipedia.org/w/api.php?action=query&format=json&prop=&list=search&formatversion=2&srsearch={search_term}&srlimit=1&srinfo=totalhits"

def get_hits(search_term):
    sleep(0.03)
    rq = requests.get(rq_url(search_term))
    try:
        return rq.json()["query"]["searchinfo"]["totalhits"]
    except KeyError:
        print(f"(Coherence) No results in search for '{search_term}', returning 0")
        return 0
#normalized wiki distance
def NWD(term1, term2, cached_requests = {}):
    N = 6942644000 #get_hits("the")
    x = cached_requests[term1] = cached_requests.get(term1,get_hits(term1))
    y = cached_requests[term2] = cached_requests.get(term2,get_hits(term2))
    xy = cached_requests[f"{term1} {term2}"] = cached_requests[f"{term2} {term1}"] = cached_requests.get(f"{term1} {term2}",get_hits(f"{term1} {term2}")) 
    
    if x == 0 or y == 0 or xy == 0:
        return 1 #float("inf")

    log_N = log(N,2)
    log_x = log(x,2)
    log_y = log(y,2)
    log_xy = log(xy,2)
    return ( max(log_x,log_y) - log_xy) / (log(N,2) - min(log_x, log_y))


def EntityCoherence(dataset):
    if isinstance(dataset,Dataset):
        documents = dataset.documents
    elif isinstance(dataset,list):
        documents = dataset
    elif isinstance(dataset,Document):
        documents = [dataset]
    else:
        raise "Invalid Input dataset"
    
    # Number of results for "the", proxy for total pages
    #N = get_hits("the")# 6942644000
        
    cached_requests = {}

    dataset_NWD_micro = 0 #all entities
    dataset_NWD_macro = 0 #averaged over documents
    entities_count = 0

    for document in documents:
        entities_count += len(document.entities)

        doc_sum_nwd = 0
        for i in range(len(document.entities)):
            e = document.entities[i].kb_link
            eb = document.entities[i-1 if i - 1 >= 0 else i + 1].kb_link
            ef = document.entities[i+1 if i + 1 < len(document.entities) else i - 1].kb_link

            neighbourNWD = (NWD(e,eb,cached_requests) + NWD(e,ef,cached_requests)) / 2
            doc_sum_nwd += neighbourNWD
            #print(neighbourNWD) 

        dataset_NWD_micro += doc_sum_nwd #entities sum
        dataset_NWD_macro += doc_sum_nwd/len(document.entities) #document nwd

    dataset_NWD_micro /= entities_count
    dataset_NWD_macro /= len(documents)
    print(f"micro:{dataset_NWD_micro}, macro:{dataset_NWD_macro}")

 

