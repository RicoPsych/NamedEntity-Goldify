from pipeline.Metrics import Metrics
from pipeline.VisualisationPipeline import VisualisationPipeline 
from visualisation.LatexGenerator import GenerateLatexComparisonTable

# wikiner_fr =  r"D:\Informatyka\Magisterka\code\NamedEntity-Goldify\results\wikiner-fr"
elgold =  r"D:\Informatyka\Magisterka\code\NamedEntity-Goldify\results\elgold\elgold"
elgold_raw =  r"D:\Informatyka\Magisterka\code\NamedEntity-Goldify\results\elgold\elgold-annotated-raw"
elgold_authors =  r"D:\Informatyka\Magisterka\code\NamedEntity-Goldify\results\elgold\elgold-verified-by-authors"
elgold_team =  r"D:\Informatyka\Magisterka\code\NamedEntity-Goldify\results\elgold\elgold-verified-by-verification-team"

voxEl_en_gold =  r"D:\Informatyka\Magisterka\code\NamedEntity-Goldify\results\categorizedVoxEL"
voxElr_en =  r"D:\Informatyka\Magisterka\code\NamedEntity-Goldify\results\rVoxEL-en"

voxEls_en =  r"D:\Informatyka\Magisterka\code\NamedEntity-Goldify\results\sVoxEL-en"
voxEls_de =  r"D:\Informatyka\Magisterka\code\NamedEntity-Goldify\results\sVoxEL-de"
voxEls_es =  r"D:\Informatyka\Magisterka\code\NamedEntity-Goldify\results\sVoxEL-es"
voxEls_fr =  r"D:\Informatyka\Magisterka\code\NamedEntity-Goldify\results\sVoxEL-fr"

wikiner_fr =  r"D:\Informatyka\Magisterka\code\NamedEntity-Goldify\results\wikiner-fr"
wikiner_fr_gold =  r"D:\Informatyka\Magisterka\code\NamedEntity-Goldify\results\wikiner-fr-gold"

metrics_full = [Metrics.GrammarCorrectness, Metrics.OccurenceKB, Metrics.OccurenceClass , Metrics.DispersityCtx, Metrics.DispersityAnnot,  Metrics.Coherence, Metrics.Consistency, Metrics.Completeness]
metrics_kb = [Metrics.GrammarCorrectness, Metrics.OccurenceKB , Metrics.DispersityCtx, Metrics.DispersityAnnot,  Metrics.Coherence, Metrics.Consistency, Metrics.Completeness]
metrics_class = [Metrics.GrammarCorrectness, Metrics.OccurenceClass , Metrics.DispersityCtx, Metrics.DispersityAnnot,  Metrics.Coherence, Metrics.Consistency, Metrics.Completeness]
# metrics = [Metrics.DispersityAnnot, Metrics.DispersityCtx]

pipeline_full = VisualisationPipeline(metrics_full, occurrence_top_n=20)
pipeline_kb = VisualisationPipeline(metrics_kb, occurrence_top_n=20)
pipeline_class = VisualisationPipeline(metrics_class, occurrence_top_n=20)

# pipeline_full.visualise_datasets([elgold,elgold_raw,elgold_authors,elgold_team])
# pipeline_kb.visualise_datasets([voxEl_en_gold, voxEls_en, voxElr_en, voxEls_de, voxEls_es, voxEls_fr])
# pipeline_class.visualise_datasets([wikiner_fr, wikiner_fr_gold])


# GenerateLatexComparisonTable([elgold,elgold_authors,elgold_team,elgold_raw], "")
#GenerateLatexComparisonTable([wikiner_fr_gold, wikiner_fr], "")

GenerateLatexComparisonTable([voxEl_en_gold, voxElr_en, voxEls_en], "") #                   <99999
#GenerateLatexComparisonTable([voxEls_en, voxEls_de, voxEls_es, voxEls_fr], "")