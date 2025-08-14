from models.Document import Document

class Dataset:
    def __init__(self, path, documents, name):
        self.path = path
        self.documents = documents
        self.name = name
    type: str
    name: str
    path: str
    documents: list[Document]
