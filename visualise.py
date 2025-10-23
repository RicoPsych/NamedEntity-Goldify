from pipeline.Metrics import Metrics
from pipeline.VisualisationPipeline import VisualisationPipeline 
from visualisation.LatexGenerator import GenerateLatexComparisonTable

results_dir = r""

# wikiner_fr =  results_dir+r"\wikiner-fr"
elgold =  results_dir+r"\elgold\elgold"
elgold_raw =  results_dir+r"\elgold\elgold-annotated-raw"
elgold_authors =  results_dir+r"\elgold\elgold-verified-by-authors"
elgold_team =  results_dir+r"\elgold\elgold-verified-by-verification-team"

voxEl_en_gold =  results_dir+r"\categorizedVoxEL"
voxElr_en =  results_dir+r"\rVoxEL-en"
voxElr_de =  results_dir+r"\rVoxEL-de"
voxElr_es =  results_dir+r"\rVoxEL-es"
voxElr_fr =  results_dir+r"\rVoxEL-fr"

voxEls_en =  results_dir+r"\sVoxEL-en"
voxEls_de =  results_dir+r"\sVoxEL-de"
voxEls_es =  results_dir+r"\sVoxEL-es"
voxEls_fr =  results_dir+r"\sVoxEL-fr"

wikiner_fr =  results_dir+r"\wikiner-fr"
wikiner_fr_gold =  results_dir+r"\wikiner-fr-gold"

metrics_full = [Metrics.GrammarCorrectness, Metrics.OccurenceKB, Metrics.OccurenceClass , Metrics.DispersityCtx, Metrics.DispersityAnnot,  Metrics.Coherence, Metrics.Consistency, Metrics.Completeness]
metrics_kb = [Metrics.GrammarCorrectness, Metrics.OccurenceKB , Metrics.DispersityCtx, Metrics.DispersityAnnot,  Metrics.Coherence, Metrics.Consistency, Metrics.Completeness]
metrics_class = [Metrics.GrammarCorrectness, Metrics.OccurenceClass , Metrics.DispersityCtx, Metrics.DispersityAnnot,  Metrics.Coherence, Metrics.Consistency, Metrics.Completeness]
# metrics = [Metrics.DispersityAnnot, Metrics.DispersityCtx]

pipeline_full = VisualisationPipeline(metrics_full, occurrence_top_n=20)
pipeline_kb = VisualisationPipeline(metrics_kb, occurrence_top_n=20)
pipeline_class = VisualisationPipeline(metrics_class, occurrence_top_n=20)

# pipeline_full.visualise_datasets([elgold,elgold_raw,elgold_authors,elgold_team])
# pipeline_kb.visualise_datasets([voxEl_en_gold, voxEls_en, voxElr_en, voxEls_de, voxEls_es, voxEls_fr])
# pipeline_kb.visualise_datasets([voxEl_en_gold, voxEls_en, voxElr_en])
# pipeline_class.visualise_datasets([wikiner_fr, wikiner_fr_gold])

# pipeline_kb.visualise_datasets([voxElr_en, voxElr_en, voxElr_de, voxElr_es, voxElr_fr])

GenerateLatexComparisonTable([elgold,elgold_authors,elgold_team,elgold_raw])
#GenerateLatexComparisonTable([wikiner_fr_gold, wikiner_fr])

#GenerateLatexComparisonTable([voxEl_en_gold, voxElr_en, voxEls_en]) #                   

#GenerateLatexComparisonTable([voxElr_en, voxElr_de, voxElr_es, voxElr_fr])
#GenerateLatexComparisonTable([voxEls_en, voxEls_de, voxEls_es, voxEls_fr])
