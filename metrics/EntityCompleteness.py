from models.Dataset import Dataset
from models.Document import Document
from models.Entity import Entity

def EntityCompleteness(dataset):
    if isinstance(dataset,Dataset):
        documents = dataset.documents
    elif isinstance(dataset,list) and isinstance(dataset[0],Document):
        documents = dataset
    elif isinstance(dataset,Document):
        documents = [dataset]
    else:
        raise "Invalid Input dataset"


