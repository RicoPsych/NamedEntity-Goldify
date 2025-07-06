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

def vector_quality_euclidean(vector, other_vectors):
    if len(other_vectors) == 0: #no other vectors then it must have perfect relative placement
        return (1,1,1) 
    
    min_distance = float("inf")
    max_distance = float("-inf")
    mean_distance = 0
    for other_vector in other_vectors:
        d = numpy.linalg.norm(vector - other_vector)
        min_distance = min(min_distance, d)
        max_distance = max(max_distance, d)
        mean_distance += d

    mean_distance /= len(other_vectors)
    return numpy.array([min_distance/max_distance, min_distance/mean_distance, mean_distance/max_distance]) # closer to 0 -> the same, closer to 1 -> different

def vector_quality_angular(vector, other_vectors, center_of_mass):
    if len(other_vectors) == 0: #no other vectors then it must have perfect relative placement
        return (1,1,1) 
    
    min_distance = float("inf")
    max_distance = float("-inf")
    mean_distance = 0
    #center_of_mass = numpy.sum([vector]+ other_vectors ,axis=0) / (len(other_vectors)+1)

    for other_vector in other_vectors:
        cosine = get_cosine(vector-center_of_mass, other_vector-center_of_mass) #/ (numpy.linalg.norm(vector-center_of_mass) * numpy.linalg.norm(other_vector-center_of_mass))
        dissimilarity = (1 - cosine) / 2
        min_distance = min(min_distance, dissimilarity)
        max_distance = max(max_distance, dissimilarity)
        mean_distance += dissimilarity

    mean_distance /= len(other_vectors)
    return numpy.array([min_distance/max_distance , min_distance/mean_distance , mean_distance/max_distance])

def vector_dispersity_euclidean(vectors):
    mean_euclidian = numpy.array([0,0,0], dtype='float64') 

    for i in range(len(vectors)):
        vec_quality_euclidean = vector_quality_euclidean(vectors[i], vectors[:i] + vectors[i+1:])
        mean_euclidian += vec_quality_euclidean        

    mean_euclidian /= len(vectors)
    return mean_euclidian

#lack of entities causes errors. (cannot sum vectors)
def vector_dispersity_angular(vectors):
    center_of_mass = numpy.sum(vectors ,axis=0) / (len(vectors))
    mean_angular = numpy.array([0,0,0], dtype='float64') 

    for i in range(len(vectors)):
        vec_quality_angular = vector_quality_angular(vectors[i], vectors[:i] + vectors[i+1:], center_of_mass)
        mean_angular += vec_quality_angular      
          
    mean_angular /= len(vectors)
    return mean_angular


def AnnotationDispersity(dataset, results_path = None):
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
    for document in tqdm.tqdm(documents):
        #Entites as vectors
        entities_names = [e.kb_name for e in document.entities] #[e.surface_form for e in document.entities]
        for name in entities_names:
            unique_entities[name] = unique_entities.get(name,sbert.encode(name))

        document_entities_vectors = [unique_entities[name] for name in entities_names]
        documents_entities_vectors.append(document_entities_vectors)
    
    #Get all entitites
    all_entities_vectors = [vector for document_vectors in documents_entities_vectors for vector in document_vectors]

    #Full macro dispersity
    macro_dispersity = 0
    macro_dispersity_angular = 0
    for document_vectors in documents_entities_vectors:
        macro_dispersity += vector_dispersity_euclidean(document_vectors)
        macro_dispersity_angular += vector_dispersity_angular(document_vectors)
    
    #full macro dispersity
    macro_dispersity /= len(documents)
    macro_dispersity_angular /= len(documents_entities_vectors)

    #Full micro dispersities
    mean_entities = vector_dispersity_euclidean(all_entities_vectors)
    mean_entities_angular = vector_dispersity_angular(all_entities_vectors)
    
    #Unique micro dispersities
    mean_unique_entities = vector_dispersity_euclidean(list(unique_entities.values()))
    mean_unique_entities_angular = vector_dispersity_angular(list(unique_entities.values()))

    print("Done")

    # print(f"Dataset all({len(all_entities_vectors)}) macro annotation dispersity: Euclidean {macro_dispersity} || Angular {macro_dispersity_angular}")
    # print(f"Dataset all({len(all_entities_vectors)}) annotation dispersity: Euclidean {mean_entities} || Angular {mean_entities_angular}")
    # print(f"Dataset unique({len(unique_entities)}) annotation dispersity: Euclidean{mean_unique_entities} || Angular {mean_unique_entities_angular}")
    return {
        "macro_dispersity":macro_dispersity.tolist(),
        "full":mean_entities.tolist(),
        "full_angular":mean_entities_angular.tolist(),
        "unique": mean_unique_entities.tolist(),
        "unique_angular": mean_unique_entities_angular.tolist()
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
    keywords_contexts_vectors  = [] 
    entities_contexts_vectors  = []
    plaintext_contexts_vectors = []

    context_vectors_similarities = []
    #Document Context Dispersity
    for document in tqdm.tqdm(documents):
        #Sum of keywords vectors as context
        keywords = [kw[0] for kw in keyword_extractor.extract_keywords(document.plain_text)]       
        #docs_keywords.append(keywords) #save keywords
        keywords_vectors = sbert.encode(keywords)
        keywords_context_vector = numpy.sum(keywords_vectors,axis=0) #sum vectors into one context vector
        keywords_contexts_vectors.append(keywords_context_vector)

        #Sum of entitites vectors as context 
        #entities_names = [e.surface_form for e in document.entities] 
        entities_names = [e.kb_name for e in document.entities] 
        entities_vectors = sbert.encode(entities_names)
        entities_context_vector = numpy.sum(entities_vectors,axis=0)
        entities_contexts_vectors.append(entities_context_vector)

        #Text vector as context
        plaintext_context_vector = sbert.encode(document.plain_text)
        # plaintext_vector_sum = numpy.sum(plaintext_vectors,axis=0)
        plaintext_contexts_vectors.append(plaintext_context_vector)

        kw_pt_similarity = get_cosine(plaintext_context_vector, keywords_context_vector)
        kw_en_similarity = get_cosine(entities_context_vector, keywords_context_vector)
        pt_en_similarity =  get_cosine(plaintext_context_vector, entities_context_vector)

        context_vectors_similarities.append({"kw_pt_similarity":kw_pt_similarity,"kw_en_similarity":kw_en_similarity,"pt_en_similarity":pt_en_similarity})

    mean_keywords = vector_dispersity_euclidean(keywords_contexts_vectors)
    mean_entities = vector_dispersity_euclidean(entities_contexts_vectors)
    mean_texts    = vector_dispersity_euclidean(plaintext_contexts_vectors) 

    mean_keywords_angular = vector_dispersity_angular(keywords_contexts_vectors)
    mean_entities_angular = vector_dispersity_angular(entities_contexts_vectors)
    mean_texts_angular    = vector_dispersity_angular(plaintext_contexts_vectors) 



    mean_similarity = {"kw_pt_similarity":0, "kw_en_similarity":0, "pt_en_similarity":0}
    for sim in context_vectors_similarities:
        mean_similarity["kw_pt_similarity"] += sim["kw_pt_similarity"]
        mean_similarity["kw_en_similarity"] += sim["kw_en_similarity"]
        mean_similarity["pt_en_similarity"] += sim["pt_en_similarity"]

    mean_similarity["kw_pt_similarity"] /= len(context_vectors_similarities)
    mean_similarity["kw_en_similarity"] /= len(context_vectors_similarities)
    mean_similarity["pt_en_similarity"] /= len(context_vectors_similarities)

    print("Done")

    # print(f"Dataset euclidean dispersity:\nKeywords: {mean_keywords}\nEntities: {mean_entities}\nTexts: {mean_texts}")
    # print(f"Dataset angular dispersity:\nKeywords: {mean_keywords_angular}\nEntities: {mean_entities_angular}\nTexts: {mean_texts_angular}")
    return {
        "context_keyword_dispersity":mean_keywords.tolist(),
        "context_entities_dispersity":mean_entities.tolist(),
        "context_text_dispersity":mean_texts.tolist(),

        "context_keyword_dispersity_angular":mean_keywords_angular.tolist(),
        "context_entities_dispersity_angular":mean_entities_angular.tolist(),
        "context_text_dispersity_angular":mean_texts_angular.tolist(),

        "context_vectors_similiarities": context_vectors_similarities,
        "mean_similarities": mean_similarity
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