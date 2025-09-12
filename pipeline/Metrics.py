from enum import Enum

class Metrics(Enum):
    GrammarCorrectness = 0
    OccurenceKB = 1
    OccurenceClass = 2
    DispersityCtx = 3
    DispersityAnnot = 4
    Completeness = 5
    Coherence = 6
    Consistency = 7
    