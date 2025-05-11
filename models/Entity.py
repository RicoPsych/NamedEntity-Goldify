
class Entity:
    def __init__(self, surface_form, class_label, kb_link, plain_start, plain_end):
        self.surface_form = surface_form
        self.class_label = class_label
        self.kb_link = kb_link
        self.plain_start = plain_start
        self.plain_end = plain_end

    token_start:int
    token_end:int

    plain_start:int
    plain_end:int

    surface_form: str
    class_label: str
    kb_link:str

    def __str__(self):
        return f"\"{self.surface_form}\" - [{self.plain_start}-{self.plain_end}], Class: {self.class_label}, KB: {self.kb_link}]  "