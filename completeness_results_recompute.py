"""Runner for Recompute Completeness"""
from pathlib import Path

from Utilities import SaveResult, SaveTable
from loaders.ElgoldLoader import ElGoldLoader
from loaders.NifLoader import NifLoader
from loaders.WikinerGoldLoader import WikinerGoldLoader
from loaders.WikinerLoader import WikinerLoader
from misc.RecomputeCompleteness import ReVisualiseCompleteness, RecomputeCompleteness
from visualisation.LatexGenerator import GenerateLatexComparisonTable


GRAMMAR = "Grammar Correctness"
COHERENCE = "Coherence"
CONSISTENCY = "Consistency"
COMPLETENESS = "Completeness"
CONTEXTDISP = "Context Dispersity"
ANNOTDISP = "Annotation Dispersity"
OCCURRENCE = "Occurrence"
OCCURRENCE_KB = "OccurrenceKB"
OCCURRENCE_CLASS = "OccurrenceClass"

metric_file_names = {
        OCCURRENCE_CLASS:"class_occurrence.json",
        OCCURRENCE_KB:"kb_occurrence.json",
        GRAMMAR:"grammar_correctness.json",
        COHERENCE:"entity_coherence.json",
        CONSISTENCY:"entity_consistency.json",
        COMPLETENESS:"entity_completeness_recomputed.json",
        CONTEXTDISP:"dispersity_contexts.json",
        ANNOTDISP:"dispersity_annotations.json"
    }

datasets_dir = r""
filename = r"entity_completeness_recomputed"
#### ELGOLD
elgold = ElGoldLoader.LoadDatasetLocal(datasets_dir+r"\elgold\elgold")
elgold_raw = ElGoldLoader.LoadDatasetLocal(datasets_dir+r"\elgold\elgold-annotated-raw")
elgold_team = ElGoldLoader.LoadDatasetLocal(datasets_dir+r"\elgold\elgold-verified-by-authors")
elgold_authors = ElGoldLoader.LoadDatasetLocal(datasets_dir+r"\elgold\elgold-verified-by-verification-team")

elgold_datasets = [ elgold ,elgold_raw ,elgold_team ,elgold_authors ]
elgold_result_path = Path("./results/elgold")
for dataset in elgold_datasets:
    entity_completeness_re = RecomputeCompleteness(dataset, elgold_result_path)
    SaveResult(entity_completeness_re, elgold_result_path / dataset.name ,filename)
    ReVisualiseCompleteness(entity_completeness_re, elgold_result_path / dataset.name / "imgs")

    pass

elgold_table = GenerateLatexComparisonTable([elgold_result_path / dataset.name for dataset in elgold_datasets])
SaveTable(elgold_table, elgold_result_path , "elgold_table")

#### WIKINER
# # # dataset_wikiner = WikinerLoader.LoadDatasetSentencesLocal(datasets_dir+r"\wikiner\5462500\aij-wikiner-fr-wp2")
dataset_wikiner_fr = WikinerLoader.LoadDatasetSentencesLocal(datasets_dir+r"\wikiner-fr-pre-gold\wikiner-fr.conll")
dataset_wikiner_gold = WikinerGoldLoader.LoadDatasetSentencesLocal(datasets_dir+r"\wikiner-fr-gold\wikiner-fr-gold.conll")

wikiner_datasets = [dataset_wikiner_fr, dataset_wikiner_gold]
wikiner_result_path = Path("./results")
for dataset in wikiner_datasets:
    entity_completeness_re = RecomputeCompleteness(dataset, wikiner_result_path)
    SaveResult(entity_completeness_re, wikiner_result_path / dataset.name, filename)
    ReVisualiseCompleteness(entity_completeness_re, wikiner_result_path / dataset.name / "imgs")

    pass
        
wikiner_table = GenerateLatexComparisonTable([wikiner_result_path / dataset.name for dataset in wikiner_datasets])
SaveTable(wikiner_table, wikiner_result_path , "wikiner_table")


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

voxel_datasets = [dataset_vox_gold, dataset_voxr_en ,dataset_voxr_de ,dataset_voxr_es ,dataset_voxr_fr ,dataset_voxs_en ,dataset_voxs_de ,dataset_voxs_es ,dataset_voxs_fr]
voxel_result_path = Path("./results")
for dataset in voxel_datasets:
    entity_completeness_re = RecomputeCompleteness(dataset, voxel_result_path)
    
    SaveResult(entity_completeness_re, voxel_result_path / dataset.name, filename)    
    ReVisualiseCompleteness(entity_completeness_re, voxel_result_path / dataset.name / "imgs")
    pass


voxel_datasets_gold_relaxed_strict = [dataset_vox_gold, dataset_voxr_en ,dataset_voxs_en]

voxel_datasets_relaxed_lang = [dataset_voxr_en ,dataset_voxr_de ,dataset_voxr_es ,dataset_voxr_fr ]
voxel_datasets_strict_lang =  [dataset_voxs_en ,dataset_voxs_de ,dataset_voxs_es ,dataset_voxs_fr ]

SaveTable(GenerateLatexComparisonTable([voxel_result_path / dataset.name for dataset in voxel_datasets_gold_relaxed_strict]), voxel_result_path , "voxel_gold_relaxed_strict_table")

SaveTable(GenerateLatexComparisonTable([voxel_result_path / dataset.name for dataset in voxel_datasets_relaxed_lang]), voxel_result_path , "voxel_relaxed_lang_table")
SaveTable(GenerateLatexComparisonTable([voxel_result_path / dataset.name for dataset in voxel_datasets_strict_lang]), voxel_result_path , "voxel_strict_lang_table")




