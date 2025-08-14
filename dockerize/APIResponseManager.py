
import json
from pathlib import Path
from Utilities import Singleton
from loaders.NifLoader import NifLoader

class APIResponseManager(metaclass=Singleton):
    available_request_types: list[str]
    global_config: dict
    
    def __init__(self, config_path = './dockerize/containerConfig.json'):
        with open(config_path, 'r') as file:
            #change docker config to absolute paths during config loading
            config_str = file.read().replace("$PWD$", str(Path.cwd()).replace("\\","\\\\"))
            self.global_config = json.loads(config_str)
            self.available_containers = list(self.global_config.keys())
            print(f"Loaded container config form: {config_path}")

    def parse_response(self, response, config_name):
        match config_name:
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

def parse_dbpedia_response(response):
    response_json = response.json()
    response_json["@text"] # text
    response_entities = response_json["Resources"] 
    entities = []
    for entity in response_entities:
        #uri = entity["@URI"]
        surface_form = entity["@surfaceForm"]
        entity_start = int(entity["@offset"])
        entity_end = int(entity["@offset"]) + len(surface_form)
        entities.append((entity_start, entity_end, surface_form))
    return entities

def parse_rel_response(response):
    entities_json = response.json()
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
