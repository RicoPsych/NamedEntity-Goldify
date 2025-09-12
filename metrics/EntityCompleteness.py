import time
from tqdm import tqdm
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
def integrate_nested_entities(new_entities_document_dict):
    for doc_entities in new_entities_document_dict:
        entities_spans = list(doc_entities)
        entities_to_remove = set()
        for i in range(len(doc_entities)):
            for n in range(len(doc_entities)):
                if i == n:
                    continue
                if entities_spans[n][0] > entities_spans[i][0]:
    #                if doc_entities[n][0][0] > doc_entities[i][0][1]: #if n entity begins after the end char of i entity, dont continue search
                    break
                if span_includes(entities_spans[n], entities_spans[i]): #if n includes i, remove i
                    doc_entities[entities_spans[n]][1] = doc_entities[entities_spans[n]][1].union(doc_entities[entities_spans[i]][1]) #union of the sets of systems that  
                    doc_entities[entities_spans[n]][0] = len(doc_entities[entities_spans[n]][1])
                    #doc_entities[n][1] += document_entities[i][1] # add the count of other entity to the longer entity
                    
                    entities_to_remove.add(entities_spans[i]) #add i to be removed 
                    break #dont check if i should be removed, move to next i
        for doc_entity in entities_to_remove:
            doc_entities.pop(doc_entity)   
    return new_entities_document_dict

def count_completeness(new_entities_docs, ners_count, gold_entity_count, per_doc_gold_entity_count):
    per_doc_thresholds = []
    dataset_thresholds = {}
    #init dataset thresholds dict with 0s
    for threshold in range(1, ners_count+1):
        dataset_thresholds[threshold] = 0
    for doc_entities in new_entities_docs:
        #init document thresholds dict with 0s
        document_thresholds = {}
        for threshold in range(1, ners_count+1):
            document_thresholds[threshold] = 0
        per_doc_thresholds.append(document_thresholds)
        for entity_span in doc_entities:
            #add higher thresholds counts to lower thresholds counts (if 3 ners agree so do 2) 
            entity_threshold = doc_entities[entity_span][0]
            for threshold in range(1, entity_threshold+1):
#                entity_threshold = entity[1]/ners_count
                dataset_thresholds[threshold] = dataset_thresholds.get(threshold,0) + 1 #count all entities for each threshold
                document_thresholds[threshold] = document_thresholds.get(threshold,0) + 1

    dataset_completeness_for_thresholds = {}    
    for threshold in dataset_thresholds: 
        threshold_count = dataset_thresholds[threshold]
        percent_threshold = threshold/ners_count                    
        #gold entities / gold and new entities                
        dataset_completeness = gold_entity_count / (threshold_count + gold_entity_count) if threshold_count != 0 else 1 #if no new entities -> completeness is 1
        dataset_completeness_for_thresholds[percent_threshold] = dataset_completeness 
    
    per_doc_completeness_for_thresholds = [] 
    for doc_i in range(len(per_doc_thresholds)):
        doc_thresholds = per_doc_thresholds[doc_i]
        doc_gold_entity_count = per_doc_gold_entity_count[doc_i]
        doc_completeness_for_thresholds = {}
        per_doc_completeness_for_thresholds.append(doc_completeness_for_thresholds)
        for threshold in doc_thresholds: 
            threshold_count = doc_thresholds[threshold]
            percent_threshold = threshold/ners_count        
            #gold entities / gold and new entities  
            doc_completeness = doc_gold_entity_count / (threshold_count + doc_gold_entity_count) if threshold_count != 0 else 1 #if no new entities -> completeness is 1               
            doc_completeness_for_thresholds[percent_threshold] = doc_completeness
    
    result = {
        "completeness": dataset_completeness_for_thresholds,
        "completeness_per_document": per_doc_completeness_for_thresholds,
    }
    return result

def EntityCompleteness(dataset):
    if isinstance(dataset,Dataset):
        documents = dataset.documents
    elif isinstance(dataset,list) and isinstance(dataset[0],Document):
        documents = dataset
    elif isinstance(dataset,Document):
        documents = [dataset]
    else:
        raise "Invalid Input dataset"

    manager = DockerManager()
    response_manager = NERSystemsResponseManager()
    contaiNERs_configs = manager.get_available_containers(completeness=True)
    contaiNERs_configs = contaiNERs_configs[4:] +  contaiNERs_configs[:4]#+ [contaiNERs_configs[2]]
    ner_outputs_documents = [] 
    for document in documents:
        ner_outputs_documents.append({})
    for contaiNER_config_name in tqdm(contaiNERs_configs, desc="ner systems"):
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
                    break
                except RuntimeError:
                    tries-=1
                    if tries == 0:
                        raise ConnectionError #could not get response
                    time.sleep(1)
                    tqdm.write(f"Retrying the request for {document.name} [{tries} tries left] ")


            document_entities = response_manager.parse_response(response, contaiNER_config_name, document.plain_text)
            document_entities = sorted(document_entities,key= lambda a : a[0]) #sort entities (order of entities may not be kept)
            document_entities = remove_nested_entities(document_entities) # removes nested entities in each system output
            ner_outputs_documents[document_index][contaiNER_config_name] = document_entities
            document_index+=1
        #stops docker container
        manager.stop_container(contaiNER_config_name)

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
    ners_count = len(contaiNERs_configs)
    
    strict_completeness = count_completeness(strict_new_entities_docs, ners_count, gold_entity_count, per_doc_gold_entity_count)    
    fuzzy_completeness = count_completeness(fuzzy_new_entities_docs, ners_count, gold_entity_count, per_doc_gold_entity_count)    

    tqdm.write("Done")

    fuzzy_new_entities_docs =  [dict([(' '.join(map(str,key)), [count_dict[key][0], list(count_dict[key][1])]) for key in count_dict]) for count_dict in fuzzy_new_entities_docs]
    strict_new_entities_docs = [dict([(' '.join(map(str,key)), [count_dict[key][0], list(count_dict[key][1])]) for key in count_dict]) for count_dict in strict_new_entities_docs] 

    result = {
        "strict_completeness": strict_completeness["completeness"],
        "strict_completeness_per_document": strict_completeness["completeness_per_document"],
        "fuzzy_completeness": fuzzy_completeness["completeness"],
        "fuzzy_completeness_per_document": fuzzy_completeness["completeness_per_document"],
        
        "fuzzy_new_entities_per_doc" : fuzzy_new_entities_docs,
        "strict_new_entities_per_doc" : strict_new_entities_docs
    }
    return result
    
