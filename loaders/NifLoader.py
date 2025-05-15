#from pynif import NIFCollection
from nifwrapper import *
from models.Entity import Entity
from models.Document import Document
from models.Dataset import Dataset

class NifLoader:
    def LoadDatasetLocal(path) -> Dataset:
        parser = NIFParser()

        with open(path,encoding="utf-8") as file:
            raw_text = file.read()
            wrp_gold = parser.parser_turtle(raw_text)

            docs = []

            for document in wrp_gold.documents:
    
                plain_text = document.getAttribute("nif:isString")
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

                        #Get nif classes in dict
                        for c in nif_classes:
                            c:str
                            prefix = c.split("-")[0]
                            nif_classes_dict[prefix] = c

                        #["el:Mnt","el:PoS","el:Ref","el:Olp"]
                        
                        #TODO: use nif classes to filter entities
                        # entity = Entity(surface_form,"",kb_link,start,end)
                        entity = Entity(surface_form, nif_classes_dict["el:Ref"], kb_link, start, end)
                        entities.append(entity)

                doc = Document("",plain_text,plain_text,entities)
                docs.append(doc)

        return Dataset(path, docs)
    

