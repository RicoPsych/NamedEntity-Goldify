import json
import os
import random

import concurrent.futures

from pathlib import Path
import time
from typing import Literal

import tqdm
from dockerize.DockerManager import DockerManager
from models.Dataset import Dataset
from models.Document import Document
from models.Entity import Entity

def transform_to_spacy(document:Document) -> dict:
    spacy_document = {}
    spacy_document["text"] = document.plain_text 
    spacy_document["entities"] = []
    for entity in document.entities:
        spacy_entity = (entity.plain_start, entity.plain_end, "ENTITY")
        spacy_document["entities"].append(spacy_entity)
    return spacy_document
    #{'text': 'Schedule a calendar event in Teak oaks HOA about competitions happening tomorrow', 'entities': [(0, 8, 'ACTION'), (11, 25, 'DOMAIN'), (29, 42, 'HOA'), (49, 71, 'EVENT'), (72, 80, 'DATE')]}

def request_coroutine(manager:DockerManager, dataset_spacy_name, lang):
    tqdm.tqdm.write("Consistency request sent")
    return manager.send_request_to_container("consistency_checker", [dataset_spacy_name, lang])

def EntityConsistency(dataset, chunk_num, lang:Literal["en","es","fr","de"] = "en"):
    if isinstance(dataset,Dataset):
        documents = dataset.documents
    elif isinstance(dataset,list) and isinstance(dataset[0],Document):
        documents = dataset
    elif isinstance(dataset,Document):
        documents = [dataset]
    else:
        raise "Invalid Input dataset"

    # transform dataset into spacy format, 
    # split into n chunks, save into temp folder (one file n chunks?)
    container_data_path = Path(".") / "dockerize" / "containers_data" / "spacy" /  "datasets"
    dataset_spacy_name = f"{dataset.name}_spacy.json"
    dataset_path = container_data_path / dataset_spacy_name
    
    #if not already created
    if not dataset_path.exists():
        spacy_dataset = [[] for i in range(chunk_num)] 
        for i in range(len(documents)):
            chunk_index = i % chunk_num
            spacy_document = transform_to_spacy(documents[i])
            spacy_dataset[chunk_index].append(spacy_document)
        with open(dataset_path,"w") as f:
            f.write(json.dumps(spacy_dataset))
    
    manager = DockerManager()
    container = manager.start_container("consistency_checker")
    #start request and print container logs
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(request_coroutine, manager, dataset_spacy_name, lang)
        logs_stream = container.logs(stream = True, tail=10)
        while not future.done():
            line = next(logs_stream).decode("utf-8", errors="ignore")
            tqdm.tqdm.write(line,end="")
    rq = future.result()
    result = rq.json()
    manager.stop_container("consistency_checker")
    
    # Check if it should be used as test or validation set in the article !!! - is the validation or test set even needed?
    return result