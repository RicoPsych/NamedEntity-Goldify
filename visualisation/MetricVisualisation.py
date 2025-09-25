import math
from visualisation.VisualisationUtils import load_results, get_gradient_list, get_2_gradients_list
from pathlib import Path
from typing import Literal
import matplotlib.pyplot as plt
import matplotlib.patches as patches

top_legend = { "bbox_to_anchor":(0, 1.02, 1, 0.2), "loc":"lower left","mode":"expand", "borderaxespad":0 }
right_center_legend = {"bbox_to_anchor":(1.04, 0.5), "loc":"center left", "borderaxespad":0}
left_center_legend = {"bbox_to_anchor":(-0.04, 0.5), "loc":"center left", "borderaxespad":0}


def Occurrence(results_path, save_img_path, occurrence_type:Literal["kb","class"] = "kb" , top_n = 10, kb_prefix = ""):
    #Piechart
    #hist
    results_path = Path(results_path) / f"{occurrence_type}_occurrence.json"   
    if not results_path.exists():
        raise FileNotFoundError
    save_img_path = Path(save_img_path)
    save_img_path.mkdir(exist_ok=True)

    results = load_results(Path(results_path))
    
    entities_count = results["entities_count"]
    #get names and amounts
    entities_names = list(results["absolute"])[:top_n]
    entities_amounts = [results["absolute"][name] for name in entities_names] 
    #entities_percentage = [results["relative"][name] for name in entities_names]
    rest_count = entities_count - sum(entities_amounts)
    
    entities_names = [name.removeprefix(kb_prefix) for name in entities_names]
    
    entities_amounts.append(rest_count)
    entities_names.append("Other")
        
    entities_amounts_top = entities_amounts[:top_n]
    entities_names_top = entities_names[:top_n]

    #count of entities that have the same counts
    entities_count_count = {}
    for entity in results["absolute"]:
        count = results["absolute"][entity]
        entities_count_count[count] = entities_count_count.get(count, 0) + count
        

    plt.figure()
    plt.subplot(2, 2, (1,1))
    #colors = get_gradient_list("blue", "cornflowerblue", len(entities_count_count))
    
    #colors = [get_gradient_list("red", "blue", len(entities_count_count)) ,get_gradient_list("red", "blue", len(entities_count_count))]
    #colors = [colors[i%2][i] for i in range(len(entities_count_count))]
    colors = get_2_gradients_list("green","lightgreen", "cadetblue" , len(entities_count_count))

    plt.pie(list(entities_count_count.values()),labels=list(entities_count_count.keys()), colors = colors , textprops={'fontsize': 5})
    plt.title("Entities count aggregated by count")

    plt.subplot(2, 2, (2,2))
    base_colors = ["darkcyan", "mediumturquoise"]
    colors = [base_colors[i%2] for i in range(len(entities_amounts)-1)] + ["gray"]#get_gradient_list("red", "salmon", len(entities_amounts)-1) 
    labels = ["" for _ in range(len(entities_amounts)-1)] + [entities_amounts[len(entities_amounts)-1] if entities_amounts[len(entities_amounts)-1] != 0 else ""]
    plt.pie(entities_amounts,labels=labels, colors = colors , labeldistance = 0.5, textprops={'fontsize': 8})
    plt.title(f"Top {top_n} entities count")

    plt.subplot(2, 2, (3,4))
    # for i, v in enumerate(entities_amounts_top):
    #     plt.text(i, -3.7, str(v),horizontalalignment="center")
        #plt.text(i, 0.5, str(v),horizontalalignment="center")
    plt.bar(range(len(entities_names_top)), height=entities_amounts_top, color = base_colors)
    plt.xticks(range(len(entities_names_top)),labels=entities_amounts_top, rotation="vertical")
    for i, v in enumerate(entities_names_top):
        entity_name = str(v) if len(str(v)) < 20 else  str(v)[:20] + "..."
        plt.text(i, plt.ylim()[1] * 0.1, entity_name ,horizontalalignment="center", rotation = "vertical", fontsize = 8)
    plt.title(f"Top {top_n} entities count")
    plt.tight_layout()

    path = save_img_path / f"occurence_{occurrence_type}.png" 
    #plt.show()
    plt.savefig(path)


def Grammar(results_path, save_img_path):
    #histogram of document errors - with line of average error
    results_path = Path(results_path) / "grammar_correctness.json"
    if not results_path.exists():
        raise FileNotFoundError
    save_img_path = Path(save_img_path)
    save_img_path.mkdir(exist_ok=True)
    
    results = load_results(results_path)

    documents_errors = results["errors_per_document"]
    values = list(documents_errors.values())
    not_too_many_labels = len(documents_errors) <= 20

    labels = [label if not_too_many_labels else i for i,label in enumerate(documents_errors.keys()) ]
    
    mean = results["errors_mean"]
    

    plt.figure()

    plt.bar(labels, values, color = "darkcyan")
    plt.xticks(rotation="vertical")
    plt.axhline(y=mean,linewidth=1, color='red', label=f"Mean Error Count = {mean:0.4f}")
    plt.legend(**top_legend)
#    plt.annotate(f"{mean}", (len(values)-1, mean+0.1))
    plt.xlabel("Document" if not_too_many_labels else "Document index")
    plt.ylabel("Error Count")

    path = save_img_path / "grammar.png" 
    plt.savefig(path)

    # plt.show()

def Coherence(results_path, save_img_path):
    #histogram of document coherences - with line of average micro and macro coherenece
    results_path = Path(results_path) / "entity_coherence.json"
    if not results_path.exists():
        raise FileNotFoundError
    save_img_path = Path(save_img_path)
    save_img_path.mkdir(exist_ok=True)
    
    results = load_results(results_path)

    documents_nwd = results["per_document_NWD"]
    values = list(documents_nwd.values())
    # labels = list(documents_nwd.keys())
    not_too_many_labels = len(documents_nwd) <= 20

    labels = [label if not_too_many_labels else i for i,label in enumerate(documents_nwd.keys()) ]

    micro_NWD = results["micro_NWD"]
    macro_NWD = results["macro_NWD"]
    
    plt.figure()
    plt.ylim(top=1.05)

    plt.bar(labels, values, color = "darkcyan")
    plt.xticks(rotation="vertical")
    plt.axhline(y=micro_NWD, linewidth=1, color='r', label=f"Micro NWD = {micro_NWD:0.4f}")
    plt.axhline(y=macro_NWD, linewidth=1, color='y', label=f"Macro NWD = {macro_NWD:0.4f}")
    plt.legend(**top_legend)
#    plt.annotate(f"{mean}", (len(values)-1, mean+0.1))
    plt.xlabel("Document" if not_too_many_labels else "Document index")
    plt.ylabel("NWD")
    
    path = save_img_path / "coherence.png" 
    plt.savefig(path)

    # plt.show()

def Consistency(results_path, save_img_path):
    def plot_consistency(values, average, stdev, label, color = "darkcyan"):
        plt.bar(range(len(values)), values, color = color)
        #plt.xticks(rotation="vertical")
        plt.axhline(y=average, linewidth=1, color='r', label=f"{label} = {average:0.4f}")
        # plt.axhline(y=(micro_f1 + micro_f1_stdev), linewidth=1, color='darkred', label=f"Micro f1 stdev = {micro_f1_stdev}")
        # plt.axhline(y=(micro_f1 - micro_f1_stdev), linewidth=1, color='darkred', label=f"Micro f1 stdev = {micro_f1_stdev}")
        plt.gca().add_patch(patches.Rectangle((-1, average - stdev), len(values)+1,stdev*2,color="lightcoral" , alpha=0.5 , label=f"{label} stdev = {stdev:0.4f}"))
        plt.legend(**top_legend)
    #    plt.annotate(f"{mean}", (len(values)-1, mean+0.1))
        plt.xlabel("Models")
        plt.ylabel(f"{label} score")

    def plot_for_averagetype(results,average_type :Literal["micro","macro"]):
        f1 = results[f"{average_type}_average_f1"]
        f1_stdev = results[f"{average_type}_f1_stdev"]
        f1_per_model = [model_score[f"{average_type}"]["f1"] for model_score in results["per_model_scores"]]

        precision = results[f"{average_type}_average_precision"]
        precision_stdev = results[f"{average_type}_precision_stdev"]
        precision_per_model = [model_score[f"{average_type}"]["precision"] for model_score in results["per_model_scores"]]
        
        recall = results[f"{average_type}_average_recall"]
        recall_stdev = results[f"{average_type}_recall_stdev"]
        recall_per_model = [model_score[f"{average_type}"]["recall"] for model_score in results["per_model_scores"]]
        
        average_type = average_type.capitalize()

        plt.figure(figsize=[6.4, 6.4])
        plt.subplot(10, 1, (1,2))
        plt.ylim(top=1.05)
        plot_consistency(f1_per_model, f1, f1_stdev, f"{average_type} f1")
        # plt.figure()
        plt.subplot(10, 1, (5,6))
        plt.ylim(top=1.05)
        plot_consistency(precision_per_model, precision, precision_stdev, f"{average_type} precision", color="seagreen")
        # plt.figure()
        plt.subplot(10, 1, (9,10))
        plt.ylim(top=1.05)
        plot_consistency(recall_per_model, recall, recall_stdev, f"{average_type} recall", color="steelblue")

    # std deviation is the metric 
    results_path = Path(results_path) / "entity_consistency.json"
    if not results_path.exists():
        raise FileNotFoundError
    save_img_path = Path(save_img_path)
    save_img_path.mkdir(exist_ok=True)

    results = load_results(results_path)
    #histogram of models scores - with line of dataset score? 
        
    plt.figure()
    plot_for_averagetype(results,"micro")    
    path = save_img_path / "micro_consistency.png" 
    plt.savefig(path)
    # plt.show()

    plt.figure()
    plot_for_averagetype(results,"macro")
    path = save_img_path / "macro_consistency.png" 
    plt.savefig(path)
    # plt.show()

def Completeness(results_path, save_img_path):
    #layered histogram? lower threshold layered over higher thresholds (with different colors)
    #column for each document - completeness of whole dataset for each threshold as lines
    results_path = Path(results_path) / "entity_completeness.json"
    if not results_path.exists():
        raise FileNotFoundError
    save_img_path = Path(save_img_path)
    save_img_path.mkdir(exist_ok=True)
    
    results = load_results(results_path)

    fuzzy_means = results["fuzzy_completeness"]
    strict_means = results["strict_completeness"]

    #reversed values for proper plotting (higher values plotted first, to be under the lower values so they are also visible)
    fuzzy_values = list(fuzzy_means.values())[::-1]
    strict_values = list(strict_means.values())[::-1]

    fuzzy_keys = list(fuzzy_means.keys())[::-1]
    strict_keys = list(strict_means.keys())[::-1]

    # alpha_step = 1/len(fuzzy_values)
    bar_colors = get_gradient_list("darkcyan", "lightcyan", len(fuzzy_values))

    plt.figure()
    plt.ylim(top=1.05)
    #plt.bar("fuzzy", height=1, color="gray" , alpha=0.2)
    #plt.bar("strict", height=1, color="gray" , alpha=0.2)
    plt.bar("fuzzy", height=fuzzy_values, color=bar_colors)
    for i, v in enumerate(fuzzy_values[::-1]):
        plt.text("fuzzy", 0.01 + i*0.05, f"{v:0.4f}", horizontalalignment = "center")
    
    plt.bar("strict", height=strict_values, color=bar_colors)
    for i, v in enumerate(strict_values[::-1]):
        plt.text("strict", 0.01 + i*0.05, f"{v:0.4f}", horizontalalignment = "center")
    
    #legend_patches =[patches.Patch(color='darkcyan',alpha=(i+1)*alpha_step ,label=threshold) for i,threshold in enumerate(fuzzy_means)]
    legend_patches = [patches.Patch(color=bar_colors[i], label=f"{(100*float(threshold)):0.2f}%") for i, threshold in enumerate(fuzzy_keys)] #add values for thresholds on plot? 
    plt.legend(handles=legend_patches, title=r"Completness by percentage thresholds of systems", **top_legend, ncol=len(legend_patches))
    plt.ylabel("Completeness")
    #plt.title(f"Completeness")
    plt.tight_layout()
    path = save_img_path / "completeness_full.png" 
    plt.savefig(path)
    # plt.show()

    #histogram - completeness as bars overlapped on one another, first grayed bar - the full dataset(lack of it actually) ,first the highest threshold, then others to the lower

    #one for fuzzy eval and one for strict


def plot_dispersity(dispersity, title, skip_y_label = True):
    min_max = dispersity[0]
    min_avg = dispersity[1]
    avg_max = dispersity[2]

    max_length = 1
    min_length = min_max * max_length
    avg_length = avg_max * max_length

    y_text_offset = plt.ylim()[1] * 0.05
    color_max = "darkcyan" 
    color_min = "lightcyan"
    colors = get_gradient_list(color_min, color_max, 10)

    avg_color_id = math.floor((avg_length - min_length) / (max_length - min_length)*9) if max_length - min_length != 0 else 9
    color_avg = colors[avg_color_id]

    plt.bar("Max", max_length, color=color_max, label="Max Distance")
    plt.text("Max", max_length - y_text_offset, f"{max_length:0.4f}", horizontalalignment = "center")
    plt.bar("Avg", avg_length, color=color_avg, label="Avg Distance")
    plt.text("Avg", avg_length - y_text_offset, f"{avg_length:0.4f}", horizontalalignment = "center")
    # plt.text("Avg", avg_bar + y_text_offset/5, f"{avg_max:0.4f}", horizontalalignment = "center")
    plt.bar("Min", min_length, color=color_min, label="Min Distance")
    plt.text("Min", min_length - y_text_offset, f"{min_length:0.4f}", horizontalalignment = "center")
    # plt.gca().set_aspect("equal")
    plt.grid(axis='y', alpha=0.4)
    if not skip_y_label:
        plt.ylabel("Vector distances [relative to Max]" )
    plt.title(f"{title} = {min_max:0.4f}", fontsize = 10)
    # plt.legend()


def ContextDispersity(results_path, save_img_path):
    results_path = Path(results_path) / "dispersity_contexts.json"
    if not results_path.exists():
        raise FileNotFoundError
    save_img_path = Path(save_img_path)
    save_img_path.mkdir(exist_ok=True)
    
    results = load_results(results_path)
    context_keyword_dispersity = results["context_keyword_dispersity"]
    context_entities_dispersity = results["context_entities_dispersity"]
    context_text_dispersity = results["context_text_dispersity"]

    context_keyword_dispersity_angular = results["context_keyword_dispersity_angular"]
    context_entities_dispersity_angular = results["context_entities_dispersity_angular"]
    context_text_dispersity_angular = results["context_text_dispersity_angular"]


    plt.figure(figsize=[8.4, 4.2])
    plt.subplot(1,3,1)
    plot_dispersity(context_keyword_dispersity,f"Keyword Context\ndispersity",skip_y_label=False)
    plt.subplot(1,3,2)
    plot_dispersity(context_entities_dispersity,f"Entities Context\ndispersity")
    plt.subplot(1,3,3)
    plot_dispersity(context_text_dispersity,f"Text Context\ndispersity")
    path = save_img_path / "dispersity_ctx_euclidean.png" 
    plt.savefig(path)

    plt.figure(figsize=[8.4, 4.2])
    plt.subplot(1,3,1)
    plot_dispersity(context_keyword_dispersity_angular,f"Keyword Context\nangular dispersity",skip_y_label=False)
    plt.subplot(1,3,2)
    plot_dispersity(context_entities_dispersity_angular,f"Entities Context\nangular dispersity")
    plt.subplot(1,3,3)
    plot_dispersity(context_text_dispersity_angular,f"Text Context\nangular dispersity")
    path = save_img_path / "dispersity_ctx_angular.png" 
    plt.savefig(path)

def AnnotationDispersity(results_path, save_img_path):
    results_path = Path(results_path) / "dispersity_annotations.json"
    if not results_path.exists():
        raise FileNotFoundError
    save_img_path = Path(save_img_path)
    save_img_path.mkdir(exist_ok=True)
    
    results = load_results(results_path)
    macro_dispersity_euclidean = results["macro_dispersity_euclidean"]
    micro_full_euclidean = results["micro_full_euclidean"]
    micro_unique_euclidean = results["micro_unique_euclidean"]

    macro_dispersity_angular = results["macro_dispersity_angular"]
    micro_full_angular = results["micro_full_angular"]
    micro_unique_angular = results["micro_unique_angular"]


    plt.figure(figsize=[8.4, 4.2])
    plt.subplot(1,3,1)
    plot_dispersity(macro_dispersity_euclidean,f"Macro annotation\ndispersity",skip_y_label=False)
    plt.subplot(1,3,2)
    plot_dispersity(micro_full_euclidean,f"Micro annotation\ndispersity")
    plt.subplot(1,3,3)
    plot_dispersity(micro_unique_euclidean,f"Micro unique annotation\ndispersity")
    path = save_img_path / "dispersity_annotation_euclidean.png" 
    plt.savefig(path)
    #plt.show()

    plt.figure(figsize=[8.4, 4.2])
    plt.subplot(1,3,1)
    plot_dispersity(macro_dispersity_angular,f"Macro annotation\nangular dispersity",skip_y_label=False)
    plt.subplot(1,3,2)
    plot_dispersity(micro_full_angular,f"Micro annotation\nangular dispersity")
    plt.subplot(1,3,3)
    plot_dispersity(micro_unique_angular,f"Micro unique annotation\nangular dispersity")
    path = save_img_path / "dispersity_annotation_angular.png" 
    plt.savefig(path)
    # plt.show()