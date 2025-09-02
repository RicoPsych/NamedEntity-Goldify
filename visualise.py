import visualisation.MetricVisualisation as vis
results_path =  r"D:\Informatyka\Magisterka\code\NamedEntity-Goldify\results\wikiner-fr"
img_path =      results_path + r"\imgs"


# vis.Completeness(results_path, img_path)
# vis.Occurrence(results_path, img_path, "kb", top_n=20, kb_prefix=r"https://en.wikipedia.org/wiki/")
vis.Occurrence(results_path, img_path, "class", top_n=20)
# vis.Coherence(results_path, img_path)
# vis.Grammar(results_path, img_path)
# vis.Consistency(results_path, img_path)