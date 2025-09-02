from enum import Enum
from pathlib import Path
from typing import Literal

from metrics.EntityCompleteness import EntityCompleteness
from metrics.EntityConsistency import EntityConsistency
from metrics.EntityOccurence import EntityOccurrence
from metrics.EntityCoherence import EntityCoherence
from metrics.ContextDispersity import ContextDispersity, AnnotationDispersity
from metrics.GrammarCorrectness import GrammarCorrectness 

from Utilities import SaveResult
from models.Dataset import Dataset

class Metrics(Enum):
    GrammarCorrectness = 0
    OccurenceKB = 1
    OccurenceClass = 2
    DispersityCtx = 3
    DispersityAnnot = 4
    Completeness = 5
    Coherence = 6
    Consistency = 7
    
class GoldifyPipeline:
    def __init__(self, pipeline: list[Metrics] = [0,1,3,4,5,6,7], consistency_chunks = 10, consistency_lang:Literal["en","fr","es","de"] = "en"):
        self.pipeline = pipeline
        self.consistency_chunks = consistency_chunks
        self.consistency_lang = consistency_lang

    def assess_dataset(self, dataset: Dataset, result_path = "./results"):
        result_path = Path(result_path) / dataset.name
        if not result_path.exists():
            result_path.mkdir(exist_ok=True)

        for metric in self.pipeline:
            match metric:
                case Metrics.GrammarCorrectness:
                    grammar_correctness = GrammarCorrectness(dataset)
                    SaveResult(grammar_correctness, result_path ,"grammar_correctness")
                    
                case Metrics.OccurenceClass:
                    classOccurrence = EntityOccurrence(dataset, "class")
                    SaveResult(classOccurrence, result_path ,"class_occurrence")
                
                case Metrics.OccurenceKB:
                    kbOccurence = EntityOccurrence(dataset, "kb")
                    SaveResult(kbOccurence, result_path ,"kb_occurrence")
        
                case Metrics.DispersityAnnot:
                    annot_dispersity = AnnotationDispersity(dataset)
                    SaveResult(annot_dispersity, result_path ,"annotation_dispersity")

                case Metrics.DispersityCtx:          
                    context_dispersity = ContextDispersity(dataset)
                    SaveResult(context_dispersity, result_path ,"context_dispersity")
        
                case Metrics.Completeness:
                    entity_completeness = EntityCompleteness(dataset)
                    SaveResult(entity_completeness, result_path ,"entity_completeness")

                case Metrics.Coherence:
                    entity_coherence = EntityCoherence(dataset, user_agent = 'WikipediaHitsScraper (s184546@student.pg.edu.pl)')
                    SaveResult(entity_coherence, result_path ,"entity_coherence")

                case Metrics.Consistency:
                    entity_consistency = EntityConsistency(dataset, self.consistency_chunks, self.consistency_lang)
                    SaveResult(entity_consistency, result_path ,"entity_consistency")
            