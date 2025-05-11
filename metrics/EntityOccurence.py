from models.Dataset import Dataset
from models.Document import Document

def CountOccurenceKB(dataset: Dataset):
    _entities = {}
    for doc in dataset.documents:
        for entity in doc.entities:
            _entities[entity.kb_link] = _entities.get(entity.kb_link,0) + 1

    sorted_entities = {k: v for k, v in sorted(_entities.items(), key=lambda item: item[1],reverse=True)}
    for k,v in list(zip(sorted_entities.keys(),sorted_entities.values()))[:10]:
        print(f"{k}:{v}")


def CountOccurenceKBDocument(document: Document):
    _entities = {}
    for entity in document.entities:
        _entities[entity.kb_link] = _entities.get(entity.kb_link,0) + 1

    sorted_entities = {k: v for k, v in sorted(_entities.items(), key=lambda item: item[1],reverse=True)}
    for k,v in list(zip(sorted_entities.keys(),sorted_entities.values()))[:10]:
        print(f"{k}:{v}")


def CountOccurenceClass(dataset: Dataset):
    _entities = {}
    for doc in dataset.documents:
        for entity in doc.entities:
            _entities[entity.class_label] = _entities.get(entity.class_label,0) + 1

    sorted_entities = {k: v for k, v in sorted(_entities.items(), key=lambda item: item[1],reverse=True)}
    for k,v in list(zip(sorted_entities.keys(),sorted_entities.values()))[:10]:
        print(f"{k}:{v}")


def CountOccurenceClassDocument(document: Document):
    _entities = {}
    for entity in document.entities:
        _entities[entity.class_label] = _entities.get(entity.class_label,0) + 1

    sorted_entities = {k: v for k, v in sorted(_entities.items(), key=lambda item: item[1],reverse=True)}
    for k,v in list(zip(sorted_entities.keys(),sorted_entities.values()))[:10]:
        print(f"{k}:{v}")