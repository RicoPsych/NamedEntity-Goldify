from pathlib import Path
from models.Dataset import Dataset
from models.Document import Document
from models.Entity import Entity
import json

types = ["class","kb"]
versions = ["absolute","relative"]

#Choose which field to count occurences on 
def EntityFieldSwitch(entity:Entity):
    return {
        "class":entity.class_label,
        "kb":entity.kb_link, 
    }

def EntityOccurence(dataset, aggregate_field, results_path = None):
    if isinstance(dataset,Dataset):
        documents = dataset.documents
    elif isinstance(dataset,list) and isinstance(dataset[0],Document):
        documents = dataset
    elif isinstance(dataset,Document):
        documents = [dataset]
    else:
        raise "Invalid Input dataset"

    _entities = {}
    entities_count = 0
    for doc in documents:
        for entity in doc.entities:
            key = EntityFieldSwitch(entity)[aggregate_field]
            _entities[key] = _entities.get(key,0) + 1
            entities_count += 1

    sorted_entities_count = {k: v for k, v in sorted(_entities.items(), key=lambda item: item[1], reverse=True)}
    sorted_entities_relative_count = {k: v/entities_count for k, v in sorted(_entities.items(), key=lambda item: item[1], reverse=True)}

    result = {
        "absolute":sorted_entities_count,
        "relative":sorted_entities_relative_count,
        "entities_count":entities_count
        }



    if results_path is not None:
        json_result = json.dumps(result)
        # Writing to sample.json

        Path(results_path).mkdir(parents=True, exist_ok=True)
        out_path = Path(results_path) / f"occurenceMetric_{aggregate_field}.json"

        with open(out_path, "w") as file:
            file.write(json_result)
    # for k,v in list(zip(sorted_entities_count.keys(),sorted_entities_count.values()))[:10]:
    #     print(f"{k}:{v}")

    return result

