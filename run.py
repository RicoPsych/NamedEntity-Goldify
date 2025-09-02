from loaders.ElgoldLoader import ElGoldLoader 
from loaders.NifLoader import NifLoader
from loaders.WikinerLoader import WikinerLoader 
from loaders.WikinerGoldLoader import WikinerGoldLoader 

from pipeline import GoldifyPipeline
from pipeline import Metrics

#dataset = ElGoldLoader.LoadDatasetLocal(r"D:\Informatyka\Magisterka\code\datasets\elgold\data")

# full_path = "D:\\Informatyka\\Magisterka\\code\\datasets\\niffy relabeled\\EL_exp\\Gold\\2019_05_19_KORE50.ttl"

# dataset = NifLoader.LoadDatasetLocal(r"D:\Informatyka\Magisterka\code\datasets\niffy relabeled\categorized_EMNLP_datasets\categorizedVoxEL.ttl", "https://en.wikipedia.org/wiki/")
# dataset_voxs = NifLoader.LoadDatasetLocal(r"D:\Informatyka\Magisterka\code\datasets\voxel\rVoxEL-en.ttl", "https://en.wikipedia.org/wiki/")
# dataset_voxr = NifLoader.LoadDatasetLocal(r"D:\Informatyka\Magisterka\code\datasets\voxel\sVoxEL-en.ttl", "https://en.wikipedia.org/wiki/")

full_path = r"D:\Informatyka\Magisterka\code\datasets\wikiner\5462500\aij-wikiner-fr-wp2"
dataset = WikinerLoader.LoadDatasetSentencesLocal(full_path)

full_path = r"D:\Informatyka\Magisterka\code\datasets\wikiner-fr-pre-gold\wikiner-fr.conll"
dataset = WikinerLoader.LoadDatasetSentencesLocal(full_path)

full_path = r"D:\Informatyka\Magisterka\code\datasets\wikiner-fr-gold\wikiner-fr-gold.conll"
dataset2 = WikinerGoldLoader.LoadDatasetSentencesLocal(full_path)

# new_docs = []
# zzz = 2
# for doc in dataset2.documents:
#     new_docs.append(doc)
#     if len(doc.entities) == 0:
#         zzz -= 1

#     if zzz == 0:
#         break
# dataset2.documents = new_docs
# dataset.documents = dataset.documents[:len(new_docs)]

# metrics = [Metrics.GrammarCorrectness, Metrics.OccurenceKB , Metrics.DispersityCtx, Metrics.DispersityAnnot, Metrics.Completeness, Metrics.Coherence ,Metrics.Consistency]
# metrics = [Metrics.OccurenceClass , Metrics.DispersityCtx, Metrics.DispersityAnnot] #quick
# metrics = [Metrics.DispersityAnnot ] #quick , Metrics.GrammarCorrectness
metrics2 = [Metrics.DispersityCtx, Metrics.DispersityAnnot ] #quick , Metrics.GrammarCorrectness
#metrics = [Metrics.Completeness] #mid 
#metrics = [Metrics.Coherence, Metrics.Consistency] #long
# metrics = [Metrics.OccurenceKB] 
# metrics = [Metrics.Consistency]
# pipeline = GoldifyPipeline(metrics, consistency_lang="fr")
pipeline2 = GoldifyPipeline(metrics2, consistency_lang="fr")
pipeline2.assess_dataset(dataset, "./results")
pipeline2.assess_dataset(dataset2, "./results")


pass