"""
Misc script, used to fix the error in Completeness metric.
Loads already existing results for Completeness from json files, 
recreates the systems' output and reruns the completeness computations 
Fixed issues with fuzzy completeness, should be proprely agregated and integrated  
"""
from collections import defaultdict
import json
from pathlib import Path
from matplotlib import patches, pyplot as plt
from tqdm import tqdm


from metrics.EntityCompleteness import align_entities_spans, count_completeness, count_entities_in_outputs, integrate_nested_entities, spans_intersects
from models.Dataset import Dataset
from models.Document import Document
from visualisation.VisualisationUtils import get_gradient_list

def LoadCompletenessResults(file_path):
    results = {}
    with open(file_path, "r") as file:
        results = json.loads(file.read()) 

    output_reconstruction = {}
    ner_list = set()

    strict_entities_docs = results["strict_new_entities_per_doc"]
    for doc_idx, doc_dict in enumerate(strict_entities_docs):
        output_reconstruction[doc_idx] = defaultdict(list)
        doc_entites:list[str] = list(doc_dict.keys())
        for doc_entity in doc_entites:
            [entity_start,entity_end, surface_form] = doc_entity.split(" ", maxsplit=2)
            [ner_amount, doc_ner_list] = doc_dict[doc_entity]
            entity = (int(entity_start),int(entity_end), surface_form)
            
            for ner in doc_ner_list:
                ner_list.add(ner)
                output_reconstruction[doc_idx][ner].append(entity)
        #output_reconstruction[doc_idx] = dict(output_reconstruction[doc_idx])
    return output_reconstruction, len(ner_list)


def RecomputeCompleteness(dataset, result_path):
    if isinstance(dataset,Dataset):
        documents = dataset.documents
    elif isinstance(dataset,list) and isinstance(dataset[0],Document):
        documents = dataset
    elif isinstance(dataset,Document):
        documents = [dataset]
    else:
        raise "Invalid Input dataset"

    completeness_result_path = Path(result_path) / dataset.name / "entity_completeness.json"
    ner_outputs_documents, ners_count  = LoadCompletenessResults(completeness_result_path)
    for i in range(len(documents)):
        document = documents[i]
        for ner in ner_outputs_documents[i]:
            ner_outputs_documents[i][ner] = align_entities_spans(document,ner_outputs_documents[i][ner])
    

    strict_new_entities_docs = []
    fuzzy_new_entities_docs = []
    for i in range(len(documents)):
        document = documents[i]
        #Probably Redundant, the results already were parsed
        gold_entities = [(entity.plain_start, entity.plain_end, entity.surface_form) for entity in document.entities]
        for g_entity in gold_entities:
            for ner_name in ner_outputs_documents[i]:
                p_entities = ner_outputs_documents[i][ner_name] 
                if g_entity in p_entities:
                    ner_outputs_documents[i][ner_name].remove(g_entity)
        ## -------------------------------------------------
        strict_output_entities_dict = count_entities_in_outputs(ner_outputs_documents[i])
        
        #fuzzy matching, actually required - the loaded results take only the strict data 
        #check if gold entities were fuzzily predicted, if so remove them
        for g_entity in gold_entities:
            for ner_name in ner_outputs_documents[i]:
                p_entities = ner_outputs_documents[i][ner_name] 
                entities_to_remove = set()
                for n in range(len(p_entities)):
                    p_entity = p_entities[n]
                    if p_entity[0] > g_entity[1]: #if predicted entity begins after the end char of gold entity, dont continue search
                        break
                    if spans_intersects(g_entity,p_entity):
                        entities_to_remove.add(p_entity) #save which entities to remove to a set (no duplicates)
                for p_entity in entities_to_remove: #remove the entities
                    ner_outputs_documents[i][ner_name].remove(p_entity) #use absolute reference to remove

        fuzzy_output_entities_dict = count_entities_in_outputs(ner_outputs_documents[i])

        strict_new_entities_docs.append(strict_output_entities_dict)
        fuzzy_new_entities_docs.append(fuzzy_output_entities_dict)

    # #remove entities that are included in other entities (no nested entities), keep the count and add it to the longest entity
    fuzzy_new_entities_docs = integrate_nested_entities(fuzzy_new_entities_docs)

    gold_entity_count = 0
    per_doc_gold_entity_count = [] 
    for document in documents:
        doc_entities_count = len(document.entities)
        gold_entity_count += doc_entities_count
        per_doc_gold_entity_count.append(doc_entities_count)
    #ners_count = len(contaiNERs_configs)
    
    strict_completeness = count_completeness(strict_new_entities_docs, ners_count, gold_entity_count, per_doc_gold_entity_count)    
    fuzzy_completeness = count_completeness(fuzzy_new_entities_docs, ners_count, gold_entity_count, per_doc_gold_entity_count)    

    tqdm.write("Done")

    fuzzy_new_entities_docs =  [dict([(' '.join(map(str,key)), [count_dict[key][0], list(count_dict[key][1])]) for key in count_dict]) for count_dict in fuzzy_new_entities_docs]
    strict_new_entities_docs = [dict([(' '.join(map(str,key)), [count_dict[key][0], list(count_dict[key][1])]) for key in count_dict]) for count_dict in strict_new_entities_docs] 

    result = {
        #whole dataset
        "strict_completeness": strict_completeness["completeness"],
        "strict_amount_per_threshold": strict_completeness["amounts_per_threshold"],
        "strict_amount_of_new_entities": sum(strict_completeness["amounts_per_threshold"].values()),

        "fuzzy_completeness": fuzzy_completeness["completeness"],
        "fuzzy_amount_per_threshold": fuzzy_completeness["amounts_per_threshold"],
        "fuzzy_amount_of_new_entities": sum(fuzzy_completeness["amounts_per_threshold"].values()),

        #per doc
        "strict_completeness_per_document": strict_completeness["completeness_per_document"],
        "strict_amount_per_doc_per_threshold" : strict_completeness["amounts_per_document_per_threshold"],
        "fuzzy_completeness_per_document": fuzzy_completeness["completeness_per_document"],
        "fuzzy_amount_per_doc_per_threshold" : fuzzy_completeness["amounts_per_document_per_threshold"],

        #per doc new entities lists
        "strict_new_entities_per_doc" : strict_new_entities_docs,
        "fuzzy_new_entities_per_doc" : fuzzy_new_entities_docs,
    }
    return result

from visualisation.MetricVisualisation import top_legend
def ReVisualiseCompleteness(results, save_img_path):
    #layered histogram? lower threshold layered over higher thresholds (with different colors)
    #column for each document - completeness of whole dataset for each threshold as lines

    save_img_path = Path(save_img_path)
    save_img_path.mkdir(exist_ok=True)
    
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
    path = save_img_path / "recomputed_completeness_full.png" 
    plt.savefig(path)
    # plt.show()

    #histogram - completeness as bars overlapped on one another, first grayed bar - the full dataset(lack of it actually) ,first the highest threshold, then others to the lower

    #one for fuzzy eval and one for strict
