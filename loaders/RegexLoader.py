import tqdm
from models.Document import Document 
from models.Entity import Entity
from models.Dataset import Dataset
import os
import re
from pathlib import Path

class ElGoldLoader:
    def LoadDatasetLocal(path):
        print(f"Loading dataset: {path}")
        doc_names = os.listdir(path)
        documents = []
        for doc_name in tqdm.tqdm(doc_names):
            full_path = Path(path) / doc_name
            with open(full_path,encoding="utf-8") as file:
                raw_text = file.read()
                documents.append(ElGoldLoader.LoadDoc(doc_name,raw_text))
        
        dataset = Dataset(path,documents)
        return dataset

    def LoadDoc(name, raw_text:str) -> Document: #regex, delimiter ,
        regex = "{{[^{}]*}}"
        delimiter = "|"

        entities = []
        plain_text = raw_text
        
        raw_entities = re.findall(regex, raw_text)
        for raw_entity in raw_entities:
            entity_as_list = raw_entity.replace(regex[0],"").replace(regex[-1],"").split(delimiter)
            
            plain_start = plain_text.find(raw_entity)
            plain_end = plain_start + len(entity_as_list[0])
            plain_text = plain_text.replace(raw_entity,entity_as_list[0],1)

            surface_form = entity_as_list[0]
            class_label = entity_as_list[1]
            kb_link = kb_name = entity_as_list[2]


            entity = Entity(surface_form,class_label,kb_link,kb_name,plain_start,plain_end)
            entities.append(entity)
            #print(entity)
        
        #token_text = plain_text.split(" ")
        
        # print(plain_text)
        doc = Document(name,raw_text,plain_text,entities)
        return doc
    
    