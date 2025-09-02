import tqdm
from models.Document import Document 
from models.Entity import Entity
from models.Dataset import Dataset
import os
import re
from pathlib import Path

class BIOESLoader:
    # def LoadDatasetSentencesLocal(path):
    #     print(f"Loading dataset: {path}")

    #     documents = []
    #     full_path = Path(path)
    #     with open(full_path,encoding="utf-8") as file:
    #         raw_text = file.read()
    #         documents_texts = [ doc_raw for doc_raw in raw_text.split("\n\n") if doc_raw != ""]
    #         documents = BIOESLoader.LoadDocuments(documents_texts,token_delimiter=" ", tag_delimiter="|")
        
    #     name = Path(path).stem
    #     dataset = Dataset(path, documents, name)
    #     return dataset


    def LoadDocuments(documents_raw, token_delimiter, tag_delimiter):
        documents = []
        for i, document_text in tqdm.tqdm(enumerate(documents_raw)):
            if document_text == "":
                continue
            doc = BIOESLoader.LoadDoc(f"{i}", document_text, token_delimiter, tag_delimiter)
            documents.append(doc)
        return documents

    
    def LoadDoc(name, raw_text, token_delimiter,tag_delimiter) -> Document: #regex, delimiter ,
        tokens_raw = raw_text.split(token_delimiter)

        plain_text = ""
        entities = []
        document_length = 0

        previous_start = -1
        previous_end = -1
        previous_class = ""
        for t, token_raw in enumerate(tokens_raw):
            token = token_raw.split(tag_delimiter)
            #if I,E - start/keep saveing entity, 
            #if B,S - save previous entity and start new
            #if O save previous entity
            surface_form = token[0]
            plain_start = document_length
            #plain_end = document_length + len(surface_form)
            class_label = token[2][2:]  

            token_tag = token[2][0]
            if  token_tag == "O" or token_tag == "B" or token_tag == "S":
                if (previous_end - previous_start) != 0:
                    previous_surface_form = plain_text[previous_start:previous_end]
                    entity = Entity(previous_surface_form, previous_class,"","",previous_start,previous_end)
                    entities.append(entity)
                    previous_class=""
                    previous_start=-1
                    previous_end=-1
                    #previous_surface_form=""
            if token_tag == "B" or token_tag == "I" or token_tag == "E" or token_tag == "S":
                previous_class = class_label
                if previous_start == -1: #new entity
                    previous_start = plain_start
                previous_end = document_length + len(surface_form)

            plain_text += surface_form + " "
            document_length = len(plain_text)

        #save last entity (if there is one)
        if (previous_end - previous_start) != 0:
            previous_surface_form = plain_text[previous_start:previous_end]
            entity = Entity(previous_surface_form, previous_class,"","",previous_start,previous_end)
            entities.append(entity)

        
        # print(plain_text)
        doc = Document(name,raw_text,plain_text,entities)
        return doc
    