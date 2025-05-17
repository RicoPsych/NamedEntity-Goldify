from loaders.RegexLoader import ElGoldLoader 
from loaders.NifLoader import NifLoader

from metrics.EntityOccurence import EntityOccurence
from metrics.EntityCoherence import EntityCoherence
from metrics.ContextDispersity import ContextDispersity

dataset = ElGoldLoader.LoadDatasetLocal("D:\\Informatyka\\Magisterka\\code\\datasets\\elgold\\data")
# print("Top10Doc:")
# CountOccurenceClassDocument(dataset.documents[0])
# CountOccurenceKBDocument(dataset.documents[0])

# print("Top10Dataset:")
# CountOccurenceClass(dataset)
# CountOccurenceKB(dataset)

#full_path = "D:\\Informatyka\\Magisterka\\code\\datasets\\niffy relabeled\\EL_exp\\Gold\\2019_05_19_KORE50.ttl"
# full_path = "D:\\Informatyka\\Magisterka\\code\\datasets\\niffy relabeled\\categorized_EMNLP_datasets\\categorizedVoxEL.ttl"
# dataset = NifLoader.LoadDatasetLocal(full_path)

#kbOccurence = EntityOccurence(dataset, "kb", "")
# classOccurence = CountOccurence(dataset, "class")
# coherence = EntityCoherence(dataset.documents[1:2])
# print(coherence)

dispersity = ContextDispersity(dataset)

pass