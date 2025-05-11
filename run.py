from loaders.RegexLoader import ElGoldLoader 
from loaders.NifLoader import NifLoader

from metrics.EntityOccurence import CountOccurenceClass, CountOccurenceClassDocument,CountOccurenceKB, CountOccurenceKBDocument

dataset = ElGoldLoader.LoadDatasetLocal("D:\Informatyka\Magisterka\code\datasets\elgold\data")
print("Top10Doc:")
CountOccurenceClassDocument(dataset.documents[0])
CountOccurenceKBDocument(dataset.documents[0])

print("Top10Dataset:")
CountOccurenceClass(dataset)
CountOccurenceKB(dataset)
# CountOccurence(dataset)

#full_path = "D:\\Informatyka\\Magisterka\\code\\datasets\\niffy relabeled\\EL_exp\\Gold\\2019_05_19_KORE50.ttl"
# full_path = "D:\\Informatyka\\Magisterka\\code\\datasets\\niffy relabeled\\categorized_EMNLP_datasets\\categorizedVoxEL.ttl"
# dataset = NifLoader.LoadDatasetLocal(full_path)

# dataset.documents[0].printEntities()
# CountOccurence(dataset)

pass