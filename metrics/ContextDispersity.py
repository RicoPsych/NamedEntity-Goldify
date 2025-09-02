from models.Dataset import Dataset
from models.Document import Document
from models.Entity import Entity

import gensim.downloader

from sentence_transformers import SentenceTransformer
import numpy
import yake
import tqdm

def get_cosine(vec1,vec2):
    return numpy.dot(vec1, vec2) / (numpy.linalg.norm(vec1) * numpy.linalg.norm(vec2))

def create_empty_cache(vectors_num):
    cache = numpy.empty((vectors_num),dtype='object')
    for row in range(vectors_num):
        cache[row] = numpy.empty((row + 1), dtype='float32')
        cache[row].fill(numpy.nan)
    return cache

def write_cache(cache, i:int, j:int, value):
    if i > j:
        smaller = j
        bigger = i
    else:
        smaller = i
        bigger = j
    cache[bigger][smaller] = value
    
def get_cached(cache, i:int, j:int):
    if i < j:
        smaller = i
        bigger = j
    else:
        smaller = j
        bigger = i
    return cache[bigger][smaller]
##deprecated
# def vector_quality_euclidean(vector, other_vectors):
#     if len(other_vectors) == 0: #no other vectors then it must have perfect relative placement
#         return (1,1,1) 
    
#     min_distance = float("inf")
#     max_distance = float("-inf")
#     mean_distance = 0
#     for other_vector in other_vectors:
#         d = numpy.linalg.norm(vector - other_vector)
#         min_distance = min(min_distance, d)
#         max_distance = max(max_distance, d)
#         mean_distance += d

#     mean_distance /= len(other_vectors)
#     return numpy.array([min_distance/max_distance, min_distance/mean_distance, mean_distance/max_distance]) # closer to 0 -> the same, closer to 1 -> different

def vector_quality_euclidean(vector_i, vectors, cache):
    if len(vectors) <= 2: #no other vectors then it must have perfect relative placement
        return (1,1,1) 
    
    min_distance = float("inf")
    max_distance = float("-inf")
    mean_distance = 0
    vector = vectors[vector_i]
    for j, other_vector in enumerate(vectors):
        if j == vector_i:
            continue

        d = get_cached(cache, vector_i, j)
        if numpy.isnan(d):
            d = numpy.linalg.norm(vector - other_vector)
            write_cache(cache, vector_i, j, d)

        min_distance = min(min_distance, d)
        max_distance = max(max_distance, d)
        mean_distance += d

    mean_distance /= (len(vectors) - 1)
    min_max_quality = min_distance/max_distance  if max_distance != 0.0 else 0.0
    min_avg_quality = min_distance/mean_distance if mean_distance != 0.0 else 0.0
    avg_max_quality = mean_distance/max_distance if max_distance != 0.0 else 0.0
    return numpy.array([min_max_quality, min_avg_quality, avg_max_quality]) # closer to 0 -> the same, closer to 1 -> different (which is better)

##DEPRACATED
# def vector_quality_angular(vector, other_vectors, center_of_mass):
#     if len(other_vectors) == 0: #no other vectors then it must have perfect relative placement
#         return (1,1,1) 
    
#     min_distance = float("inf")
#     max_distance = float("-inf")
#     mean_distance = 0
#     #center_of_mass = numpy.sum([vector]+ other_vectors ,axis=0) / (len(other_vectors)+1)

#     for other_vector in other_vectors:
#         cosine = get_cosine(vector-center_of_mass, other_vector-center_of_mass) #/ (numpy.linalg.norm(vector-center_of_mass) * numpy.linalg.norm(other_vector-center_of_mass))
#         dissimilarity = (1 - cosine) / 2
#         min_distance = min(min_distance, dissimilarity)
#         max_distance = max(max_distance, dissimilarity)
#         mean_distance += dissimilarity

#     mean_distance /= len(other_vectors)
#     return numpy.array([min_distance/max_distance , min_distance/mean_distance , mean_distance/max_distance])

def vector_quality_angular(vector_i, vectors, center_of_mass, cache):
    if len(vectors) <= 2: #if no more than 2 vectors then it must have perfect relative placement
        return (1,1,1) 
    
    min_distance = float("inf")
    max_distance = float("-inf")
    mean_distance = 0
    #center_of_mass = numpy.sum([vector]+ other_vectors ,axis=0) / (len(other_vectors)+1)
    vector = vectors[vector_i]
    for j, other_vector in enumerate(vectors):
        if j == vector_i:
            continue
        
        dissimilarity = get_cached(cache, vector_i, j)
        if numpy.isnan(dissimilarity):
            cosine = get_cosine(vector-center_of_mass, other_vector-center_of_mass) #/ (numpy.linalg.norm(vector-center_of_mass) * numpy.linalg.norm(other_vector-center_of_mass))
            dissimilarity = (1 - cosine) / 2
            write_cache(cache, vector_i, j, dissimilarity)

        min_distance = min(min_distance, dissimilarity)
        max_distance = max(max_distance, dissimilarity)
        mean_distance += dissimilarity

    mean_distance /= (len(vectors) - 1)
    min_max_quality = min_distance/max_distance  if max_distance != 0.0 else 0.0
    min_avg_quality = min_distance/mean_distance if mean_distance != 0.0 else 0.0
    avg_max_quality = mean_distance/max_distance if max_distance != 0.0 else 0.0
    return numpy.array([min_max_quality, min_avg_quality, avg_max_quality]) # closer to 0 -> the same, closer to 1 -> different (which is better)

def vector_dispersity_euclidean(vectors, disable_logging = False):
    mean_euclidian = numpy.array([0,0,0], dtype='float64') 
    
    cache = create_empty_cache(len(vectors))
    for i in tqdm.tqdm(range(len(vectors)),desc="Vectors", disable=disable_logging):
        vec_quality_euclidean = vector_quality_euclidean(i, vectors, cache)
        mean_euclidian += vec_quality_euclidean        

    mean_euclidian /= len(vectors)
    return mean_euclidian

#lack of entities causes errors. (cannot sum vectors)
# vector eq 0.0 also causes errors
def vector_dispersity_angular(vectors,disable_logging = False):
    #filiter out notvectors (empty / non-existent vectors)
    center_of_mass = numpy.sum([vector for vector in vectors if type(vector) is numpy.ndarray], axis=0) / (len(vectors))
    mean_angular = numpy.array([0,0,0], dtype='float64') 
    
    cache = create_empty_cache(len(vectors))
    for i in tqdm.tqdm(range(len(vectors)), desc="Vectors", disable=disable_logging):
        #for empty vectors use the average value of quality
        if type(vectors[i]) is numpy.ndarray:
            vec_quality_angular = vector_quality_angular(i, vectors, center_of_mass, cache)
            mean_angular += vec_quality_angular
        else:
            mean_angular += 0.5      
          
    mean_angular /= len(vectors)
    return mean_angular


def AnnotationDispersity(dataset):
    if isinstance(dataset,Dataset):
        documents = dataset.documents
    elif isinstance(dataset,list) and isinstance(dataset[0],Document):
        documents = dataset
    elif isinstance(dataset,Document):
        documents = [dataset]
    else:
        raise "Invalid Input dataset"
    
    print("Annotation Dispersity")

    print("Loading SentenceTransformer Model")
    sbert = SentenceTransformer("all-mpnet-base-v2")
    print("Loaded SentenceTransformer")

    #Parse Documents
    documents_entities_vectors  = []
    unique_entities = {}
    documents_without_entities = 0
    for document in tqdm.tqdm(documents,desc="Documents"):
        #skip docs without entities
        if (len(document.entities) == 0):
            documents_without_entities +=1
            continue
        #Entites as vectors
        entities_names = [e.kb_name if e.kb_name != "" else e.surface_form for e in document.entities] #[e.surface_form for e in document.entities]
        for name in entities_names:
            unique_entities[name] = unique_entities.get(name,sbert.encode(name))

        document_entities_vectors = [unique_entities[name] for name in entities_names]
        documents_entities_vectors.append(document_entities_vectors)
    
    #Get all entitites
    all_entities_vectors = [vector for document_vectors in documents_entities_vectors for vector in document_vectors]

    #Full macro dispersity
    print("Macro dispersity")
    macro_dispersity = 0
    macro_dispersity_angular = 0
    for document_vectors in tqdm.tqdm(documents_entities_vectors, desc="Documents"):
        macro_dispersity += vector_dispersity_euclidean(document_vectors, disable_logging=True)
        macro_dispersity_angular += vector_dispersity_angular(document_vectors, disable_logging=True)
    
    #full macro dispersity
    macro_dispersity /= len(documents_entities_vectors)
    macro_dispersity_angular /= len(documents_entities_vectors)

    #Full micro dispersities
    print("Micro dispersity")
    mean_entities = vector_dispersity_euclidean(all_entities_vectors)
    mean_entities_angular = vector_dispersity_angular(all_entities_vectors)
    all_entities_count = len(all_entities_vectors)

    #Unique micro dispersities
    print("Micro unique dispersity")
    mean_unique_entities = vector_dispersity_euclidean(list(unique_entities.values()))
    mean_unique_entities_angular = vector_dispersity_angular(list(unique_entities.values()))
    unique_entities_count = len(unique_entities)

    print("Done")

    return {
        "macro_dispersity_euclidean":macro_dispersity.tolist(),
        "macro_dispersity_angular":macro_dispersity_angular.tolist(),
        "micro_full_euclidean":mean_entities.tolist(),
        "micro_full_angular":mean_entities_angular.tolist(),
        "micro_unique_euclidean": mean_unique_entities.tolist(),
        "micro_unique_angular": mean_unique_entities_angular.tolist(),
        "documents_without_entities": documents_without_entities, #skipped documents in metrics
        "unique_entities_count": unique_entities_count,
        "all_entities_count": all_entities_count 
    }    

def ContextDispersity(dataset, results_path = None):
    if isinstance(dataset,Dataset):
        documents = dataset.documents
    elif isinstance(dataset,list) and isinstance(dataset[0],Document):
        documents = dataset
    elif isinstance(dataset,Document):
        documents = [dataset]
    else:
        raise "Invalid Input dataset"
    
    print("Context Dispersity")

    # Load https://huggingface.co/sentence-transformers/all-mpnet-base-v2
    print("Loading SentenceTransformer Model")
    sbert = SentenceTransformer("all-mpnet-base-v2")
    print("Loaded SentenceTransformer")

    #ngram 3, top 10 keywords
    keyword_extractor = yake.KeywordExtractor(n=3, top=10)

    #docs_keywords = [] 
    keywords_contexts_vectors  = [] #TODO: swap for np.arrays
    entities_contexts_vectors  = [] #TODO: swap for np.arrays
    plaintext_contexts_vectors = [] #TODO: swap for np.arrays

    context_vectors_similarities = []
    #Document Context Dispersity
    documents_without_entities = 0
    for document in tqdm.tqdm(documents, desc="Documents"):
        #Sum of keywords vectors as context
        keywords = [kw[0] for kw in keyword_extractor.extract_keywords(document.plain_text)]       
        keywords_vectors = sbert.encode(keywords)
        keywords_context_vector = numpy.sum(keywords_vectors,axis=0) #sum vectors into one context vector
        keywords_contexts_vectors.append(keywords_context_vector)

        #Sum of entitites vectors as context, skip the document if no entities are provided?
        if len(document.entities) != 0: #skip if there are no entities in the document
            entities_names = [e.kb_name if e.kb_name != "" else e.surface_form for e in document.entities] 
            entities_vectors = sbert.encode(entities_names)
            entities_context_vector = numpy.sum(entities_vectors,axis=0)
            entities_contexts_vectors.append(entities_context_vector)
        else:
            entities_context_vector = 0.0
            documents_without_entities += 1

        #Text vector as context
        plaintext_context_vector = sbert.encode(document.plain_text)
        plaintext_contexts_vectors.append(plaintext_context_vector)

        #if the unable to compute vector, the similarities are 0
        kw_pt_similarity = float(get_cosine(plaintext_context_vector, keywords_context_vector)) if type(plaintext_context_vector) is numpy.ndarray and type(keywords_context_vector) is numpy.ndarray else 0.0
        kw_en_similarity = float(get_cosine(entities_context_vector, keywords_context_vector))  if type(entities_context_vector)  is numpy.ndarray and type(keywords_context_vector) is numpy.ndarray else 0.0
        pt_en_similarity = float(get_cosine(plaintext_context_vector, entities_context_vector)) if type(plaintext_context_vector) is numpy.ndarray and type(entities_context_vector) is numpy.ndarray else 0.0

        context_vectors_similarities.append({"kw_pt_similarity":kw_pt_similarity,"kw_en_similarity":kw_en_similarity,"pt_en_similarity":pt_en_similarity})

    print("Keywords ctx vectors")
    mean_keywords = vector_dispersity_euclidean(keywords_contexts_vectors)
    mean_keywords_angular = vector_dispersity_angular(keywords_contexts_vectors)
    print("Entities ctx vectors")
    mean_entities = vector_dispersity_euclidean(entities_contexts_vectors)
    mean_entities_angular = vector_dispersity_angular(entities_contexts_vectors)
    print("Plain text ctx vectors")
    mean_texts = vector_dispersity_euclidean(plaintext_contexts_vectors) 
    mean_texts_angular = vector_dispersity_angular(plaintext_contexts_vectors) 

    mean_similarity = {"kw_pt_similarity":0, "kw_en_similarity":0, "pt_en_similarity":0}
    for sim in context_vectors_similarities:
        mean_similarity["kw_pt_similarity"] += sim["kw_pt_similarity"]
        mean_similarity["kw_en_similarity"] += sim["kw_en_similarity"]
        mean_similarity["pt_en_similarity"] += sim["pt_en_similarity"]

    mean_similarity["kw_pt_similarity"] /= len(context_vectors_similarities)
    mean_similarity["kw_en_similarity"] /= len(context_vectors_similarities)
    mean_similarity["pt_en_similarity"] /= len(context_vectors_similarities)

    print("Done")
    return {
        "context_keyword_dispersity":mean_keywords.tolist(),
        "context_entities_dispersity":mean_entities.tolist(),
        "context_text_dispersity":mean_texts.tolist(),

        "context_keyword_dispersity_angular":mean_keywords_angular.tolist(),
        "context_entities_dispersity_angular":mean_entities_angular.tolist(),
        "context_text_dispersity_angular":mean_texts_angular.tolist(),

        "documents_without_entities":documents_without_entities, #skipped in entities dispersity
        "documents_count": len(documents),

        "mean_similarities": mean_similarity,
        "context_vectors_similiarities": context_vectors_similarities
    }    
    
    # print("Loading Word2Vec Model")
    # glove300 = gensim.downloader.load("glove-wiki-gigaword-300")
    # print("Loaded")


    # #anims = ["dog", "cat", "fish",  "bird", "bird"]
    # anims = ["dog", "cat", "tiger",  "wolf", "bird"]
    

    # vectors = model.encode(anims)
    # vectors_glove = [glove300[v] for v in anims]
    
    # for i in range(len(anims)):
    #     print(anims[i])
    #     print(anims[:i] + anims[i+1:])

    #     a = vectors[:i].tolist()
    #     b = vectors[i+1:].tolist()
    #     print("SBERT:")
    #     print(vector_quality(vectors[i], a+b))
    #     print("Glove:")
    #     print(vector_quality(vectors_glove[i],vectors_glove[:i] + vectors_glove[i+1:]))

    #pass



# CHECK SIMILARITY BETWEEN TEXT AND KEYWORD VECTORS