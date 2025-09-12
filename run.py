from dockerize.DockerManager import DockerManager
from loaders.ElgoldLoader import ElGoldLoader 
from loaders.NifLoader import NifLoader
from loaders.WikinerLoader import WikinerLoader 
from loaders.WikinerGoldLoader import WikinerGoldLoader 

from pipeline.GoldifyPipeline import GoldifyPipeline
from pipeline.GoldifyPipeline import Metrics

# elgold = ElGoldLoader.LoadDatasetLocal(r"D:\Informatyka\Magisterka\code\datasets\elgold\elgold")
# elgold_raw = ElGoldLoader.LoadDatasetLocal(r"D:\Informatyka\Magisterka\code\datasets\elgold\elgold-annotated-raw")
# elgold_team = ElGoldLoader.LoadDatasetLocal(r"D:\Informatyka\Magisterka\code\datasets\elgold\elgold-verified-by-authors")
# elgold_authors = ElGoldLoader.LoadDatasetLocal(r"D:\Informatyka\Magisterka\code\datasets\elgold\elgold-verified-by-verification-team")

# #Metrics.GrammarCorrectness, Metrics.OccurenceKB, Metrics.OccurenceClass , Metrics.DispersityCtx, Metrics.DispersityAnnot,  Metrics.Coherence, Metrics.Consistency, Metrics.Completeness
# metrics_full = []
# pipeline = GoldifyPipeline(metrics_full, consistency_lang="en")
# pipeline.assess_datasets([elgold ,elgold_raw, elgold_team, elgold_authors], "./results/elgold")

# # # # dataset_wikiner = WikinerLoader.LoadDatasetSentencesLocal(r"D:\Informatyka\Magisterka\code\datasets\wikiner\5462500\aij-wikiner-fr-wp2")
dataset_wikiner_fr = WikinerLoader.LoadDatasetSentencesLocal(r"D:\Informatyka\Magisterka\code\datasets\wikiner-fr-pre-gold\wikiner-fr.conll")
dataset_wikiner_gold = WikinerGoldLoader.LoadDatasetSentencesLocal(r"D:\Informatyka\Magisterka\code\datasets\wikiner-fr-gold\wikiner-fr-gold.conll")

# err_doc = [dataset for dataset in dataset_wikiner_fr.documents if dataset.plain_text.find("Painlev") != -1]
# dataset_wikiner_fr.documents = err_doc
# rsp = DockerManager().send_request_to_container("rel",err_doc.plain_text)

# # # metrics_disp = [Metrics.DispersityAnnot]
pipeline = GoldifyPipeline([Metrics.Completeness], consistency_lang="fr", user_agent= 'WikipediaHitsScraper (s184546@student.pg.edu.pl)')
pipeline.assess_datasets([dataset_wikiner_fr,dataset_wikiner_gold]) #dataset_wikiner_fr

# metrics = [Metrics.GrammarCorrectness]
# pipeline = GoldifyPipeline(metrics, consistency_lang="fr")
# pipeline.assess_dataset(dataset_wikiner_gold) #Copied
# # pipeline.assess_dataset(dataset_wikiner_fr) # Done


# # # metrics_dispersity = [Metrics.DispersityAnnot, Metrics.DispersityCtx ]
# # # pipeline = GoldifyPipeline(metrics_dispersity, consistency_lang="fr")
# # # pipeline.assess_dataset(dataset_wikiner_gold)


#NifLoader
# full_path = "D:\\Informatyka\\Magisterka\\code\\datasets\\niffy relabeled\\EL_exp\\Gold\\2019_05_19_KORE50.ttl"

# dataset_vox_gold = NifLoader.LoadDatasetLocal(r"D:\Informatyka\Magisterka\code\datasets\niffy relabeled\categorized_EMNLP_datasets\categorizedVoxEL.ttl", "https://en.wikipedia.org/wiki/")
# # dataset_voxs = NifLoader.LoadDatasetLocal(r"D:\Informatyka\Magisterka\code\datasets\voxel\rVoxEL-en.ttl", "https://en.wikipedia.org/wiki/")
# dataset_voxr = NifLoader.LoadDatasetLocal(r"D:\Informatyka\Magisterka\code\datasets\voxel\sVoxEL-en.ttl", "https://en.wikipedia.org/wiki/")
# metrics_full_kb = [Metrics.GrammarCorrectness, Metrics.OccurenceKB , Metrics.DispersityCtx, Metrics.DispersityAnnot, Metrics.Completeness, Metrics.Coherence, Metrics.Consistency]

# pipeline_full = GoldifyPipeline(metrics_full_kb, consistency_lang="en")
# # pipeline_full.assess_dataset(dataset_vox_gold, "./results")
# pipeline_full.assess_dataset(dataset_voxr, "./results")


pass