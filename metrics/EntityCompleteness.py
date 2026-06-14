from collections import defaultdict
import time
from tqdm import tqdm
from Utilities import find_closest_substr
from dockerize.APIResponseManager import NERSystemsResponseManager
from dockerize.DockerManager import DockerManager
from models.Dataset import Dataset
from models.Document import Document
from models.Entity import Entity
import json

def spans_intersects(self: tuple[int,int], other: tuple[int,int]):
        exlcusive = (other[0] > self[1] and other[1] > self[1]) or (other[1] < self[0] and other[0] < self[0]  )
        return not exlcusive

def span_includes(self: tuple[int,int], other: tuple[int,int]):
        include = (self[0] <= other[0] and self[1] >= other[1]) and (self[0] <= other[1] and self[1] >= other[0])
        return include

def count_entities_in_outputs(document_ner_output_dict):
    counted_output_entities_dict = {}
    for ner_name in document_ner_output_dict:
        for entity in document_ner_output_dict[ner_name]:
            entity_list = counted_output_entities_dict.get(entity, [0,set()])
            entity_list[1].add(ner_name)
            entity_list[0] = len(entity_list[1])
            counted_output_entities_dict[entity] = entity_list #counted_output_entities_dict.get(entity,0) + 1
    #by default tuples are sorted by 1st item 
    sorted_output_entities_dict = dict([(key, counted_output_entities_dict[key]) for key in sorted(counted_output_entities_dict, key = lambda x : counted_output_entities_dict.get(x)[0], reverse=True)]) 
    return sorted_output_entities_dict

def remove_nested_entities(document_entities):
    entities_to_remove = set()
    for i in range(len(document_entities)):
        for n in range(len(document_entities)):
            if i == n:
                continue
            if document_entities[n][0] > document_entities[i][1]: #if n entity begins after the end char of i entity, dont continue search
                break
            if span_includes(document_entities[n],document_entities[i]): #if n includes i, remove i
                entities_to_remove.add(document_entities[i]) #add i to be removed 
                break #dont check if i should be removed, move to next i
    for doc_entity in entities_to_remove:
        document_entities.remove(doc_entity)   
    return document_entities

#integrates entities included in other entities into the entities with larger spans, transfers systems that recognized them and adds them to the entitiy system count
#check if entity spans intersect
#   if so, integrate them
#   else keep them seperate
def integrate_nested_entities(list_of_document_dicts_of_entities):
    for idx in range(len(list_of_document_dicts_of_entities)):
        doc_entities = list_of_document_dicts_of_entities[idx]
        entities_spans = list(doc_entities.keys())

        aggregated_entities = set()
        entities_to_keep = defaultdict(list) 
        #new entities - mapped to list of old ones 
        #:keys: - keeped entities, :value: - list of old entities to integrate
        for i in range(len(doc_entities)):
            if (i in aggregated_entities): #if already aggregated, skip
                continue
            keep_entity_span = entities_spans[i] #new agregate entity
            keep_entity_old_list = set() #set of old entities to be agregated
            keep_entity_old_list.add(entities_spans[i])
            
            for n in range(len(doc_entities)): # checks up to i
                if (i == n) or (n in aggregated_entities): # skip if already checked,
                    continue
                n_entity_spans = entities_spans[n]

                # if n_entity_spans[0] > keep_entity_span[1]: #if n begins after i ends - don't check more n -> next i will be this n
                #     break

                if spans_intersects(n_entity_spans, keep_entity_span):
                    #if intersects - get the widest span - union of n and i
                    new_start = min(entities_spans[n][0], entities_spans[i][0])
                    new_end = max(entities_spans[n][1], entities_spans[i][1])
                    new_len = new_end - new_start

                    start_string = entities_spans[n][2] if new_start == entities_spans[n][0] else entities_spans[i][2] 
                    end_string = entities_spans[n][2] if new_end == entities_spans[n][1] else entities_spans[i][2]
                    new_surface_form = start_string

                    difference = new_len - len(start_string)
                    if difference > 0:
                        new_surface_form += end_string[-difference:] 

                    keep_entity_span = (new_start,new_end, new_surface_form) #new joined form 
                    aggregated_entities.add(n_entity_spans)                   #set n as aggregated
                    keep_entity_old_list.add(n_entity_spans)                  #set n to be joined with others aggregated in the new form

            entities_to_keep[keep_entity_span] = keep_entity_old_list
        #aggregate old entities into new spans
        new_doc_entities = {}
        for new_span, old_entities in entities_to_keep.items():
            new_entity_stats = [0,set] 
            for old_entity in old_entities:
                new_entity_stats[1] = new_entity_stats[1].union(doc_entities[old_entity][1]) #union of the sets of systems that  
            new_entity_stats[0] = len(new_entity_stats[1])

            new_doc_entities[new_span] = new_entity_stats
        #swap doc dict with new doc dict, sorted by ner count - descending
        sorteddict = {k: v for k, v in sorted(new_doc_entities.items(), key=lambda item: item[1][0], reverse=True)}        
        list_of_document_dicts_of_entities[idx] = sorteddict
        
        # for tests, sort by start index
        # __sorteddict = {k: v for k, v in sorted(new_doc_entities.items(), key=lambda item: item[0][0])}
        # pass

    return list_of_document_dicts_of_entities
    
                #### OLD
    #             if entities_spans[n][0] > entities_spans[i][1]:
    # #                if doc_entities[n][0][0] > doc_entities[i][0][1]: #if n entity begins after the end char of i entity, dont continue search
    #                 break
    #             if span_includes(entities_spans[n], entities_spans[i]): #if n includes i, 
    #                 doc_entities[entities_spans[n]][1] = doc_entities[entities_spans[n]][1].union(doc_entities[entities_spans[i]][1]) #union of the sets of systems that  
    #                 doc_entities[entities_spans[n]][0] = len(doc_entities[entities_spans[n]][1])
    #                 #doc_entities[n][1] += document_entities[i][1] # add the count of other entity to the longer entity
                    
    #                 aggregated_entities.add(entities_spans[i]) #add i to be removed 
    #                 #dont check if i should be removed, move to next i
    #                 continue 
                
    #             if spans_intersects(entities_spans[n], entities_spans[i]): 
    #                 #if n intersects with i, union n and i, remove change n to new, set i to be removed

    #                 a = entities_spans[n]
    #                 b = entities_spans[i]
    #                 if entities_spans[i][2] == entities_spans[n][2]: #if intersects, but has the same Surface form - remove the less found (probably error)
    #                     n_ners = doc_entities[entities_spans[n]][0]
    #                     i_ners = doc_entities[entities_spans[i]][0]
    #                     if n_ners >= i_ners:
    #                         doc_entities[entities_spans[n]][1] = doc_entities[entities_spans[n]][1].union(doc_entities[entities_spans[i]][1]) #union of the sets of systems that  
    #                         doc_entities[entities_spans[n]][0] = len(doc_entities[entities_spans[n]][1])
                  
    #                         aggregated_entities.add(entities_spans[i]) #remove i
    #                         break
    #                     else:
    #                         doc_entities[entities_spans[i]][1] = doc_entities[entities_spans[i]][1].union(doc_entities[entities_spans[n]][1]) #union of the sets of systems that  
    #                         doc_entities[entities_spans[i]][0] = len(doc_entities[entities_spans[i]][1])
 
    #                         aggregated_entities.add(entities_spans[n]) #remove n
    #                         continue

    #                 #if intersects - get the widest span - union of n and i
    #                 new_start = min(entities_spans[n][0], entities_spans[i][0])
    #                 new_end = max(entities_spans[n][1], entities_spans[i][1])
    #                 new_len = new_end - new_start

    #                 start_string = entities_spans[n][2] if new_start == entities_spans[n][0] else entities_spans[i][2] 
    #                 end_string = entities_spans[n][2] if new_end == entities_spans[n][1] else entities_spans[i][2]
    #                 difference = new_len - len(start_string)
    #                 if difference > 0:
    #                     new_surface_form = start_string + end_string[-difference:] 
    #                 #else start_string


    #                 ###???

    #                 # doc_entities[entities_spans[n]][1] = doc_entities[entities_spans[n]][1].union(doc_entities[entities_spans[i]][1]) #union of the sets of systems that  
    #                 # doc_entities[entities_spans[n]][0] = len(doc_entities[entities_spans[n]][1])
    #                 # #doc_entities[n][1] += document_entities[i][1] # add the count of other entity to the longer entity
                    
    #                 aggregated_entities.add(entities_spans[i]) #add i to be removed 
    #                 break #dont check if i should be removed, move to next i
        
        # for doc_entity in aggregated_entities:
        #     doc_entities.pop(doc_entity)   
    return list_of_document_dicts_of_entities

def count_completeness(new_entities_docs, ners_count, gold_entity_count, per_doc_gold_entity_count):
    per_doc_thresholds = []
    dataset_thresholds = defaultdict(int)
    #init dataset thresholds dict with 0s
    # for threshold in range(1, ners_count+1):
    #     dataset_thresholds[threshold] = 0
    for doc_entities in new_entities_docs:
        #init document thresholds dict with 0s
        document_thresholds = defaultdict(int)#{}
        # for threshold in range(1, ners_count+1):
        #     document_thresholds[threshold] = 0
        per_doc_thresholds.append(document_thresholds)
        for entity_span in doc_entities:
            #add higher thresholds counts to lower thresholds counts (if 3 ners agree so do 2) 
            entity_threshold = doc_entities[entity_span][0]
            for threshold in range(1, entity_threshold+1):
#                entity_threshold = entity[1]/ners_count
                dataset_thresholds[threshold] = dataset_thresholds.get(threshold,0) + 1 #count all entities for each threshold
                document_thresholds[threshold] = document_thresholds.get(threshold,0) + 1
    
    amount_of_entities_per_threshold = {}
    dataset_completeness_per_threshold = {}    
    for threshold in dataset_thresholds: 
        threshold_count = dataset_thresholds[threshold]
        percent_threshold = threshold/ners_count                    
        #gold entities / gold and new entities                
        dataset_completeness = gold_entity_count / (threshold_count + gold_entity_count) if threshold_count != 0 else 1 #if no new entities -> completeness is 1
        dataset_completeness_per_threshold[percent_threshold] = dataset_completeness 
        amount_of_entities_per_threshold[percent_threshold] = threshold_count

    per_doc_completeness_per_threshold = [] 
    per_doc_amount_of_entities_per_threshold = [] 
    for doc_i in range(len(per_doc_thresholds)):
        doc_thresholds = per_doc_thresholds[doc_i]
        doc_gold_entity_count = per_doc_gold_entity_count[doc_i]
        doc_completeness_per_threshold = {}
        doc_amount_of_entities_per_threshold = {}
        per_doc_completeness_per_threshold.append(doc_completeness_per_threshold)
        per_doc_amount_of_entities_per_threshold.append(doc_amount_of_entities_per_threshold)
        for threshold in doc_thresholds: 
            threshold_count = doc_thresholds[threshold]
            percent_threshold = threshold/ners_count        
            #gold entities / gold and new entities  
            doc_completeness = doc_gold_entity_count / (threshold_count + doc_gold_entity_count) if threshold_count != 0 else 1 #if no new entities -> completeness is 1               
            doc_completeness_per_threshold[percent_threshold] = doc_completeness
            doc_amount_of_entities_per_threshold[percent_threshold] = threshold_count

    result = {
        "completeness": dataset_completeness_per_threshold,
        "completeness_per_document": per_doc_completeness_per_threshold,
        "amounts_per_threshold": amount_of_entities_per_threshold,
        "amounts_per_document_per_threshold": per_doc_amount_of_entities_per_threshold
    }
    return result



def align_entities_spans(document:Document, document_entities:list):
    to_be_removed = []

    for entity_id in range(len(document_entities)):
        (entity_start, entity_end, surface_form) = document_entities[entity_id]
        #entity_len = entity_end - entity_start
        real_start = find_closest_substr(document.plain_text,surface_form,entity_start)
        if real_start == -1: #Not Found anywhere/ remove?
            #real_start = document.plain_text.find(surface_form)
            to_be_removed.append(entity_id)
            continue

        if real_start != entity_start:
            real_end = real_start + len(surface_form)
            document_entities[entity_id] = (real_start, real_end, surface_form)
        
    for entity_id in reversed(to_be_removed):
        print(f"Removing entity {entity_id}: {document_entities[entity_id][2]} at {document_entities[entity_id][0]}")
        document_entities.pop(entity_id)

    return document_entities

def FetchNERSystemsResults(documents):
    manager = DockerManager()
    response_manager = NERSystemsResponseManager()
    contaiNERs_configs = manager.get_available_containers(completeness=True)
    contaiNERs_configs = contaiNERs_configs[4:] +  contaiNERs_configs[:4]#+ [contaiNERs_configs[2]]
    ner_outputs_documents = [] 
    for document in documents:
        ner_outputs_documents.append({})
    for contaiNER_config_name in tqdm(contaiNERs_configs, desc="Systems"):
        #starts docker container
        manager.start_container(contaiNER_config_name)

        document_index = 0
        for document in tqdm(documents, desc="documents"): 
            tries = 3
            while tries > 0:
                try:
                    response = manager.send_request_to_container(contaiNER_config_name, document.plain_text) 
                    if response.status_code != 200:
                        tqdm.write(f"An error occured with response from {contaiNER_config_name}\n[Error Code: {response.status_code}][Request url: {response.request.url}]\ndocument name = {document.name}")
                        raise RuntimeError
                    document_entities = response_manager.parse_response(response, contaiNER_config_name, document.plain_text) #may raise value error?
                    break
                except RuntimeError:
                    tries-=1
                    if tries == 0:
                        raise ConnectionError #could not get response
                    time.sleep(1)
                    tqdm.write(f"Retrying the request for {document.name} [{tries} tries left] ")
                except ValueError:
                    tries-=1
                    if tries == 0:
                        raise ConnectionError #could not parse response
                    time.sleep(1)
                    tqdm.write(f"Retrying the request for {document.name} [{tries} tries left] ")


            document_entities = sorted(document_entities,key= lambda a : a[0]) #sort entities (order of entities may not be kept)
            document_entities = remove_nested_entities(document_entities) # removes nested entities in each system output
            document_entities = align_entities_spans(document,document_entities)
            ner_outputs_documents[document_index][contaiNER_config_name] = document_entities
            document_index+=1
        #stops docker container
        manager.stop_container(contaiNER_config_name)
    return ner_outputs_documents, len(contaiNERs_configs)

def EntityCompleteness(dataset):
    if isinstance(dataset,Dataset):
        documents = dataset.documents
    elif isinstance(dataset,list) and isinstance(dataset[0],Document):
        documents = dataset
    elif isinstance(dataset,Document):
        documents = [dataset]
    else:
        raise "Invalid Input dataset"

    ner_outputs_documents,ners_count  = FetchNERSystemsResults(documents)

    strict_new_entities_docs = []
    fuzzy_new_entities_docs = []
    for i in range(len(documents)):
        document = documents[i]
        gold_entities = [(entity.plain_start, entity.plain_end, entity.surface_form) for entity in document.entities]
        #check if gold entities were predicted, if so remove them
        #strict matching only (fuzzy matching will also remove them)
        for g_entity in gold_entities:
            for ner_name in ner_outputs_documents[i]:
                p_entities = ner_outputs_documents[i][ner_name] 
                if g_entity in p_entities:
                    ner_outputs_documents[i][ner_name].remove(g_entity)

        strict_output_entities_dict = count_entities_in_outputs(ner_outputs_documents[i])
        #fuzzy matching 
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
        "strict_completeness": strict_completeness["completeness"],
        "strict_amount_per_threshold": strict_completeness["amounts_per_threshold"],

        "fuzzy_completeness": fuzzy_completeness["completeness"],
        "fuzzy_amount_per_threshold": fuzzy_completeness["amounts_per_threshold"],
        
        "fuzzy_completeness_per_document": fuzzy_completeness["completeness_per_document"],
        "fuzzy_new_entities_per_doc" : fuzzy_new_entities_docs,
        "fuzzy_amount_per_doc_per_threshold" : fuzzy_completeness["amounts_per_document_per_threshold"],

        "strict_completeness_per_document": strict_completeness["completeness_per_document"],
        "strict_new_entities_per_doc" : strict_new_entities_docs,
        "strict_amount_per_doc_per_threshold" : strict_completeness["amounts_per_document_per_threshold"],
    }
    return result
    
