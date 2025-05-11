from models.Document import Document

class Dataset:
    def __init__(self,path,documents):
        self.path = path
        self.documents = documents
        
    type: str
    name: str
    path: str
    documents: list[Document]
