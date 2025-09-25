
from pathlib import Path
from pipeline.Metrics import Metrics
import visualisation.MetricVisualisation as vis


class VisualisationPipeline:
    def __init__(self, pipeline: list[Metrics] = [0,1,3,4,5,6,7], occurrence_top_n = 20, occurrence_kb_prefix = ""):
        self.pipeline = pipeline
        self.occurrence_top_n = occurrence_top_n
        self.occurrence_kb_prefix = occurrence_kb_prefix

    def match_metric(self, metric, results_path):
        print(f"Dataset: {results_path.stem} | {metric}")
        img_path = results_path / "imgs"
        match metric:
            case Metrics.GrammarCorrectness:
                vis.Grammar(results_path, img_path)
            case Metrics.OccurenceClass:
                vis.Occurrence(results_path, img_path, "class", top_n=self.occurrence_top_n)  
            case Metrics.OccurenceKB:
                vis.Occurrence(results_path, img_path, "kb", top_n=self.occurrence_top_n, kb_prefix=self.occurrence_kb_prefix)
            case Metrics.DispersityAnnot:
                vis.AnnotationDispersity(results_path,img_path)
            case Metrics.DispersityCtx:          
                vis.ContextDispersity(results_path, img_path)
            case Metrics.Completeness:
                vis.Completeness(results_path, img_path)
            case Metrics.Coherence:
                vis.Coherence(results_path, img_path)
            case Metrics.Consistency:
                vis.Consistency(results_path, img_path)

    def visualise_dataset(self, dataset_results_path):
        results_path = Path(dataset_results_path)
        if not results_path.exists():
            raise FileNotFoundError

        for metric in self.pipeline:
            self.match_metric(metric,results_path)  


    def visualise_datasets(self, dataset_results_paths):
        for dataset_results_path in dataset_results_paths:
            self.visualise_dataset(dataset_results_path)