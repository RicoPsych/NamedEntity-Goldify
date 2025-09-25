
import json
from pathlib import Path

import tqdm
from Utilities import Singleton
from loaders.NifLoader import NifLoader

class NERSystemsResponseManager(metaclass=Singleton):
    available_request_types: list[str]
    global_config: dict
    
    def __init__(self, config_path = './dockerize/containerConfig.json'):
        with open(config_path, 'r') as file:
            #change docker config to absolute paths during config loading
            config_str = file.read().replace("$PWD$", str(Path.cwd()).replace("\\","\\\\"))
            self.global_config = json.loads(config_str)
            self.available_containers = list(self.global_config.keys())
            tqdm.tqdm.write(f"Loaded container config form: {config_path}")

    def parse_response(self, response, config_name, document_text):
        try: #try parse
            match config_name: #try raise?
                case "spacy":
                    entities = parse_spacy_response(response)
                    return entities

                case "rel":
                    entities = parse_rel_response(response)
                    return entities

                case "stanford_ner":
                    entities = parse_stanford_ner_response(response)
                    return entities

                case "dbpedia_spotlight":
                    entities = parse_dbpedia_response(response)
                    return entities
                
                case "flair":
                    entities = parse_flair_response(response, document_text)
                    return entities
        except:
            #could not parse
            tqdm.tqdm.write(f"Could not parse response for {config_name}")
            raise ValueError

#document text is used to fix the indexing problem
#caused by the flair spliting the response into sentences 
def parse_flair_response(response, document_text):
    response_sentences_json = response.json()
    entities = []
    sentence_start = 0
    for response_sentence in response_sentences_json: 
        sentence_text = response_sentence.get("text")
        #find starting index of the sentence in document text, starting from previous sentence 
        sentence_start = document_text.find(sentence_text, sentence_start) 
        response_entities = response_sentence.get("entities",[])
        for entity in response_entities:
            surface_form = entity["text"]
            entity_start = entity["start_pos"] + sentence_start
            entity_end = entity["end_pos"] + sentence_start
            #type = entity["type"]
            entities.append((entity_start, entity_end, surface_form))
        sentence_start += len(response_sentence.get("text",""))
        #add the length of the current sentence, next starts from this id
    return entities

def parse_dbpedia_response(response):
    response_json = response.json()
    response_json["@text"] # text
    response_entities = response_json.get("Resources",[]) 
    entities = []
    for entity in response_entities:
        #uri = entity["@URI"]
        surface_form = entity["@surfaceForm"]
        entity_start = int(entity["@offset"])
        entity_end = int(entity["@offset"]) + len(surface_form)
        entities.append((entity_start, entity_end, surface_form))
    return entities

def parse_rel_response(response):
    try:
        entities_json = response.json() #try raise?
    except:
        #Could not parse rel response
        raise ValueError
    
    entities = []
    for entity in entities_json:
        #ner = entity[6]
        surface_form = entity[2]
        entity_start = int(entity[0])
        entity_end = entity_start + len(surface_form)
        entities.append((entity_start, entity_end, surface_form))
    return entities

def parse_spacy_response(response):
    entities_json = response.json()
    entities = []
    for entity in entities_json:
        #ner = entity["type"]
        surface_form = entity["text"]
        entity_start = int(entity["start"])
        entity_end = int(entity["end"])
        entities.append((entity_start, entity_end, surface_form))
    return entities

def parse_stanford_ner_response(response):
    sentences = response.json()["sentences"]
    entities = []
    for sentence in sentences: 
        sentence_entities = sentence["entitymentions"]
        for entity in sentence_entities:
            surface_form = entity["text"]
            entity_start = int(entity["characterOffsetBegin"])
            entity_end = int(entity["characterOffsetEnd"])
            #ner = entity["ner"]
            entities.append((entity_start, entity_end, surface_form))
    return entities
