from models.Entity import Entity

class Document:
    def __init__(self, name, raw_text, plain_text,entities):
        self.name = name
        self.raw_text = raw_text
        self.plain_text = plain_text
        self.entities = entities

    name:str
    raw_text:str

    plain_text: str
    token_text: list[str]
    
    entities: list[Entity] 

    def printEntities(self):
        for entity in self.entities:
            print(entity)