import tqdm
from pathlib import Path
from typing import Literal
from models.Dataset import Dataset
from models.Document import Document
from models.Entity import Entity
import Levenshtein

types = ["class","kb"]
versions = ["absolute","relative"]

#Choose which field to count occurences on 
def EntityFieldSwitch(entity:Entity):
    return {
        "class":entity.class_label,
        "kb":entity.kb_name, 
    }

def EntityOccurrence(dataset, aggregate_field: Literal["class","kb"]):
    if isinstance(dataset,Dataset):
        documents = dataset.documents
    elif isinstance(dataset,list) and isinstance(dataset[0],Document):
        documents = dataset
    elif isinstance(dataset,Document):
        documents = [dataset]
    else:
        raise "Invalid Input dataset"

    print("Entity Occurrence")

    #Count entities
    _entities = {}
    entities_count = 0
    for doc in tqdm.tqdm(documents):
        for entity in doc.entities:
            key = EntityFieldSwitch(entity)[aggregate_field]
            _entities[key] = _entities.get(key,0) + 1
            entities_count += 1

    sorted_entities_count = {k: v for k, v in sorted(_entities.items(), key=lambda item: item[1], reverse=True)}
    sorted_entities_relative_count = {k: v/entities_count for k, v in sorted(_entities.items(), key=lambda item: item[1], reverse=True)}

    #Find other entities with the closest levenshtein distances
    entities_names = list(sorted_entities_count.keys())
    entities_distances = {}
    for i, checked_entity in enumerate(entities_names):
        for ii, entity in enumerate(entities_names[(i+1):]): #check ratio of every entity after the checked_entity (no need to check previous as the ratio function is commutative)
            ratio = Levenshtein.ratio(checked_entity, entity)

            entities_distances[checked_entity] = entry_checked = entities_distances.get(checked_entity, {})
            entry_checked_ratio_list = entry_checked.get(ratio, [])
            entry_checked_ratio_list.append(entity)
            entities_distances[checked_entity][ratio] = entry_checked_ratio_list

            entities_distances[entity] = entry = entities_distances.get(entity, {})
            entry_ratio_list = entry.get(ratio, [])
            entry_ratio_list.append(checked_entity)
            entities_distances[entity][ratio] = entry_ratio_list

    #entites sorted by their occurrence
    close_entities = {}
    for entity in sorted_entities_count:
        max_ratio = max(list(entities_distances[entity].keys()))
        close_entities[entity] = [max_ratio, entities_distances[entity][max_ratio]]

    #sorted_close_entities = {k: v for k, v in sorted(close_entities.items(), key=lambda item: item[1][0], reverse=True)}

    result = {
        "absolute":sorted_entities_count,
        "relative":sorted_entities_relative_count,
        "similar_entities":close_entities,
        "entities_count":entities_count,
        }

    print("Done")

    return result

