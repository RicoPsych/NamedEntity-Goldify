from dockerize.DockerManager import DockerManager
from loaders.ElgoldLoader import ElGoldLoader 
from loaders.NifLoader import NifLoader
from loaders.WikinerLoader import WikinerLoader 
from loaders.WikinerGoldLoader import WikinerGoldLoader 

from pipeline.GoldifyPipeline import GoldifyPipeline
from pipeline.GoldifyPipeline import Metrics

user_agent = 'WikipediaHitsScraper (xxxx@xxxx.xxx)'
datasets_dir = r""

# #Metrics.GrammarCorrectness, Metrics.OccurenceKB, Metrics.OccurenceClass , Metrics.DispersityCtx, Metrics.DispersityAnnot,  Metrics.Coherence, Metrics.Consistency, Metrics.Completeness
metrics_full = [Metrics.GrammarCorrectness, Metrics.OccurenceKB, Metrics.OccurenceClass , Metrics.DispersityCtx, Metrics.DispersityAnnot, Metrics.Completeness, Metrics.Coherence, Metrics.Consistency]
metrics_el =   [Metrics.GrammarCorrectness, Metrics.OccurenceKB , Metrics.DispersityCtx, Metrics.DispersityAnnot, Metrics.Completeness, Metrics.Coherence, Metrics.Consistency]
metrics_ner =  [Metrics.GrammarCorrectness, Metrics.OccurenceClass , Metrics.DispersityCtx, Metrics.DispersityAnnot, Metrics.Completeness, Metrics.Coherence, Metrics.Consistency]

#### ELGOLD
# elgold = ElGoldLoader.LoadDatasetLocal(datasets_dir+r"\elgold\elgold")
# elgold_raw = ElGoldLoader.LoadDatasetLocal(datasets_dir+r"\elgold\elgold-annotated-raw")
# elgold_team = ElGoldLoader.LoadDatasetLocal(datasets_dir+r"\elgold\elgold-verified-by-authors")
# elgold_authors = ElGoldLoader.LoadDatasetLocal(datasets_dir+r"\elgold\elgold-verified-by-verification-team")
             
# pipeline = GoldifyPipeline([Metrics.Coherence], consistency_lang="en", user_agent = user_agent)
# pipeline.assess_datasets([elgold ,elgold_raw, elgold_team, elgold_authors], "./results/elgold")
# pipeline.assess_datasets([elgold_raw, elgold_team, elgold_authors], "./results/elgold")


#### WIKINER
# # # dataset_wikiner = WikinerLoader.LoadDatasetSentencesLocal(datasets_dir+r"\wikiner\5462500\aij-wikiner-fr-wp2")
# dataset_wikiner_fr = WikinerLoader.LoadDatasetSentencesLocal(datasets_dir+r"\wikiner-fr-pre-gold\wikiner-fr.conll")
# dataset_wikiner_gold = WikinerGoldLoader.LoadDatasetSentencesLocal(datasets_dir+r"\wikiner-fr-gold\wikiner-fr-gold.conll")

# pipeline_fr = GoldifyPipeline([Metrics.OccurenceClass], consistency_lang="fr", user_agent = user_agent)
# pipeline_fr.assess_datasets([dataset_wikiner_fr])


#### VOXEL
dataset_vox_gold = NifLoader.LoadDatasetLocal(datasets_dir+r"\niffy relabeled\categorized_EMNLP_datasets\categorizedVoxEL.ttl", kb_prefix_regex=r"^https://..\.wikipedia\.org/wiki/")
dataset_voxr_en = NifLoader.LoadDatasetLocal(datasets_dir+r"\voxel\rVoxEL-en.ttl", kb_prefix_regex=r"^https://..\.wikipedia\.org/wiki/")

dataset_voxr_de = NifLoader.LoadDatasetLocal(datasets_dir+r"\voxel\rVoxEL-de.ttl", kb_prefix_regex=r"^https://..\.wikipedia\.org/wiki/")
dataset_voxr_es = NifLoader.LoadDatasetLocal(datasets_dir+r"\voxel\rVoxEL-es.ttl", kb_prefix_regex=r"^https://..\.wikipedia\.org/wiki/")
dataset_voxr_fr = NifLoader.LoadDatasetLocal(datasets_dir+r"\voxel\rVoxEL-fr.ttl", kb_prefix_regex=r"^https://..\.wikipedia\.org/wiki/")

dataset_voxs_en = NifLoader.LoadDatasetLocal(datasets_dir+r"\voxel\sVoxEL-en.ttl", kb_prefix_regex=r"^https://..\.wikipedia\.org/wiki/")
dataset_voxs_de = NifLoader.LoadDatasetLocal(datasets_dir+r"\voxel\sVoxEL-de.ttl", kb_prefix_regex=r"^https://..\.wikipedia\.org/wiki/")
dataset_voxs_es = NifLoader.LoadDatasetLocal(datasets_dir+r"\voxel\sVoxEL-es.ttl", kb_prefix_regex=r"^https://..\.wikipedia\.org/wiki/")
dataset_voxs_fr = NifLoader.LoadDatasetLocal(datasets_dir+r"\voxel\sVoxEL-fr.ttl", kb_prefix_regex=r"^https://..\.wikipedia\.org/wiki/")

# metrics_full_kb = [Metrics.OccurenceKB , Metrics.DispersityCtx, Metrics.DispersityAnnot, Metrics.Coherence]

pipeline_fr = GoldifyPipeline(metrics_el, consistency_lang="fr", user_agent= user_agent)
pipeline_de = GoldifyPipeline(metrics_el, consistency_lang="de", user_agent= user_agent)
pipeline_es = GoldifyPipeline(metrics_el, consistency_lang="es", user_agent= user_agent)
pipeline_en = GoldifyPipeline(metrics_el, consistency_lang="en", user_agent= user_agent)

# pipeline_en.assess_dataset(dataset_vox_gold)
# pipeline_en.assess_dataset(dataset_voxr_en)

# pipeline_fr.assess_dataset(dataset_voxs_fr)
# pipeline_de.assess_dataset(dataset_voxs_de)
# pipeline_es.assess_dataset(dataset_voxs_es)
# pipeline_en.assess_dataset(dataset_voxs_en)


# pipeline_fr.assess_dataset(dataset_voxr_fr)
# pipeline_de.assess_dataset(dataset_voxr_de)
# pipeline_es.assess_dataset(dataset_voxr_es)
# pipeline_en.assess_dataset(dataset_voxr_en)



pass