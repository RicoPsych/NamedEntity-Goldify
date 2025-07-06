from dockerize.DockerManager import DockerManager
from loaders.RegexLoader import ElGoldLoader 
from loaders.NifLoader import NifLoader

from metrics.EntityOccurence import EntityOccurence
from metrics.EntityCoherence import EntityCoherence
from metrics.ContextDispersity import ContextDispersity, AnnotationDispersity
from metrics.GrammarCorrectness import GrammarCorrectness 

from Utilities import SaveResult

DockerManager() #Instantiate DockerManager Singleton

#dataset = ElGoldLoader.LoadDatasetLocal("D:\\Informatyka\\Magisterka\\code\\datasets\\elgold\\data")
# full_path = "D:\\Informatyka\\Magisterka\\code\\datasets\\niffy relabeled\\EL_exp\\Gold\\2019_05_19_KORE50.ttl"
full_path = "D:\\Informatyka\\Magisterka\\code\\datasets\\niffy relabeled\\categorized_EMNLP_datasets\\categorizedVoxEL.ttl"
dataset = NifLoader.LoadDatasetLocal(full_path, "https://en.wikipedia.org/wiki/")

# coherence = EntityCoherence(dataset.documents[1:2])
# print(coherence)

# classOccurence = EntityOccurence(dataset, "class")
# dispersity = ContextDispersity(dataset)
#kbOccurence = EntityOccurence(dataset, "kb", "")
#annot_dispersity = AnnotationDispersity(dataset)
#context_dispersity = ContextDispersity(dataset)
grammar_correctness = GrammarCorrectness(dataset)

#print(kbOccurence)
#print(annot_dispersity)
#print(context_dispersity)
print(grammar_correctness)

#SaveResult(kbOccurence, "./results" ,"kbOccurence")
#SaveResult(grammar_correctness, "./results" ,"grammar")
#SaveResult(annot_dispersity, "./results" ,"annotationDispersity")
#SaveResult(context_dispersity, "./results" ,"contextDispersity")


pass