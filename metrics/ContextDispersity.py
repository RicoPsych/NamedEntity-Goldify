from models.Dataset import Dataset
from models.Document import Document
from models.Entity import Entity

import gensim.downloader

from sentence_transformers import SentenceTransformer
import numpy

def vector_quality(vector, other_vectors):
    min_distance = float("inf")
    max_distance = float("-inf")
    mean_distance = 0
    for other_vector in other_vectors:
        d = numpy.linalg.norm(vector-other_vector)
        min_distance = min(min_distance,d)
        max_distance = max(max_distance,d)
        mean_distance += d

    mean_distance/=len(other_vectors)
    return (min_distance/max_distance , min_distance/mean_distance , mean_distance/max_distance )



def ContextDispersity(dataset, results_path = None):
    if isinstance(dataset,Dataset):
        documents = dataset.documents
    elif isinstance(dataset,list) and isinstance(dataset[0],Document):
        documents = dataset
    elif isinstance(dataset,Document):
        documents = [dataset]
    else:
        raise "Invalid Input dataset"
    
    # for document in documents:
    #     document.plain_text
    print("Loading Word2Vec Model")
    glove300 = gensim.downloader.load("glove-wiki-gigaword-300")
    print("Loaded")

    # Load https://huggingface.co/sentence-transformers/all-mpnet-base-v2
    print("Loading SentenceTransformer Model")
    model = SentenceTransformer("all-mpnet-base-v2")
    print("Loaded SentenceTransformer")

    #anims = ["dog", "cat", "fish",  "bird", "bird"]
    anims = ["dog", "cat", "tiger",  "wolf", "bird"]
    

    vectors = model.encode(anims)
    vectors_glove = [glove300[v] for v in anims]
    
    for i in range(len(anims)):
        print(anims[i])
        print(anims[:i] + anims[i+1:])

        a = vectors[:i].tolist()
        b = vectors[i+1:].tolist()
        print("SBERT:")
        print(vector_quality(vectors[i], a+b))
        print("Glove:")
        print(vector_quality(vectors_glove[i],vectors_glove[:i] + vectors_glove[i+1:]))

    pass

