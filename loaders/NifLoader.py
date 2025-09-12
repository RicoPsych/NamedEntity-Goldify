#from pynif import NIFCollection
from pathlib import Path
from nifwrapper import *
from models.Entity import Entity
from models.Document import Document
from models.Dataset import Dataset
import tqdm

class NifLoader:
    def LoadDatasetStr(raw_text, kb_prefix = ""):
        parser = NIFParser()
        wrp_gold = parser.parser_turtle(raw_text)
        docs = []
        index = 0 #for document name
        for document in tqdm.tqdm(wrp_gold.documents):
            plain_text = document.getAttribute("nif:isString").rstrip()
            entities = []
            for sentence in document.sentences:
                sentence_start = int(sentence.getAttribute("nif:beginIndex"))
                #sentence_end = sentence.getAttribute("nif:endIndex")
                for annotation in sentence.annotations:
                    start = int(annotation.getAttribute("nif:beginIndex")) + sentence_start
                    end = int(annotation.getAttribute("nif:endIndex")) + sentence_start
                    surface_form =  annotation.getAttribute("nif:anchorOf")

                    #TODO fix links, its list or others
                    kb_link =  annotation.getAttribute("itsrdf:taIdentRef")[0]
                    
                    nif_classes = annotation.getAttribute("itsrdf:taClassRef")
                    nif_classes_dict = {}
                    kb_name = kb_link.removeprefix(kb_prefix).replace("_"," ")

                    #Get nif classes in dict
                    if nif_classes is not None:
                        for c in nif_classes:
                            c:str
                            prefix = c.split("-")[0]
                            nif_classes_dict[prefix] = c
                    #["el:Mnt","el:PoS","el:Ref","el:Olp"]
                    
                    #TODO: use nif classes to filter entities
                    # entity = Entity(surface_form,"",kb_link,start,end)
                    class_label = nif_classes_dict.get("el:Ref","")
                    entity = Entity(surface_form, class_label, kb_link, kb_name, start, end)
                    entities.append(entity)
            doc = Document(index,plain_text,plain_text,entities)
            docs.append(doc)
            index+=1
        return docs
    
    def LoadDatasetRequest(text, name, kb_prefix = "") -> Dataset:
        tqdm.tqdm.write(f"Loading dataset from request")
        docs = NifLoader.LoadDatasetStr(text, kb_prefix)
        dataset = Dataset(None, docs, name)
        return dataset
    
    def LoadDatasetLocal(path, kb_prefix = "") -> Dataset:
        tqdm.tqdm.write(f"Loading dataset: {path}")
        with open(path,encoding="utf-8") as file:
            raw_text = file.read()
        docs = NifLoader.LoadDatasetStr(raw_text, kb_prefix)
        name = Path(path).stem
        dataset = Dataset(path, docs, name)
        return dataset
    

