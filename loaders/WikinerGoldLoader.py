import tqdm
from loaders.BIOESLoader import BIOESLoader
from models.Document import Document 
from models.Entity import Entity
from models.Dataset import Dataset
import os
import re
from pathlib import Path

class WikinerGoldLoader:
    def LoadDatasetLocal(path):
        tqdm.tqdm.write(f"Loading dataset: {path}")

        documents = []
        full_path = Path(path)
        with open(full_path,encoding="utf-8") as file:
            raw_text = file.read()
            documents_texts = [ doc_raw for doc_raw in raw_text.split("\n\n") if doc_raw != ""]
            documents = BIOESLoader.LoadDocuments(documents_texts, token_delimiter="\n", tag_delimiter=" ")
        
        name = Path(path).stem
        dataset = Dataset(path, documents, name)
        return dataset
    
    def LoadDatasetSentencesLocal(path):
        tqdm.tqdm.write(f"Loading dataset: {path}")

        documents = []
        full_path = Path(path)
        with open(full_path,encoding="utf-8") as file:
            raw_text = file.read()
            documents_texts = [ doc_raw for doc_raw in raw_text.split("\n\n") if doc_raw != ""]
            documents = BIOESLoader.LoadDocuments(documents_texts, token_delimiter="\n", tag_delimiter=" ")
        
        name = Path(path).stem
        dataset = Dataset(path, documents, name)
        return dataset
