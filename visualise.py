from pipeline.Metrics import Metrics
from pipeline.VisualisationPipeline import VisualisationPipeline 
# wikiner_fr =  r"D:\Informatyka\Magisterka\code\NamedEntity-Goldify\results\wikiner-fr"
elgold =  r"D:\Informatyka\Magisterka\code\NamedEntity-Goldify\results\elgold\elgold"
elgold_raw =  r"D:\Informatyka\Magisterka\code\NamedEntity-Goldify\results\elgold\elgold-annotated-raw"
elgold_authors =  r"D:\Informatyka\Magisterka\code\NamedEntity-Goldify\results\elgold\elgold-verified-by-authors"
elgold_team =  r"D:\Informatyka\Magisterka\code\NamedEntity-Goldify\results\elgold\elgold-verified-by-verification-team"


metrics = [Metrics.GrammarCorrectness, Metrics.OccurenceKB, Metrics.OccurenceClass , Metrics.DispersityCtx, Metrics.DispersityAnnot,  Metrics.Coherence, Metrics.Consistency, Metrics.Completeness]
# metrics = [Metrics.DispersityAnnot, Metrics.DispersityCtx]
pipeline = VisualisationPipeline(metrics, occurrence_top_n=20)
pipeline.visualise_dataset(elgold)
pipeline.visualise_dataset(elgold_raw)
pipeline.visualise_dataset(elgold_authors)
pipeline.visualise_dataset(elgold_team)
# vis.Completeness(results_path, img_path)
# vis.Occurrence(results_path, img_path, "kb", top_n=20, kb_prefix=r"https://en.wikipedia.org/wiki/")
# vis.Occurrence(results_path, img_path, "class", top_n=20)
# vis.Coherence(results_path, img_path)
# vis.Grammar(results_path, img_path)
# vis.Consistency(results_path, img_path)
# vis.ContextDispersity(results_path, img_path)
# vis.AnnotationDispersity(results_path,img_path)