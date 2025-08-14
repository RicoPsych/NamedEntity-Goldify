import json
import sys
import spacy
from pathlib import Path
from spacy.tokens import DocBin
from spacy.util import filter_spans
from spacy import displacy
from statistics import stdev
from tqdm import tqdm

def to_docbin(document,nlp):
    text = document['text']
    labels = document['entities']

    doc = nlp.make_doc(text)
    ents = []
    for start, end, label in labels: 
        span = doc.char_span(start, end, label=label, alignment_mode="contract")
        if span is None:
            print("Skipping entity")
        else:
            ents.append(span)
    filtered_ents = filter_spans(ents)
    doc.ents = filtered_ents
    return doc

def measure_scores_strict(predicted_docs, standard_docs):
    docs_num = len(predicted_docs)
    total_tp = 0
    total_fp = 0
    total_fn = 0

    macro_precision=0
    macro_recall=0
    macro_f1=0

    for i in range(docs_num):
        predicted = predicted_docs[i]
        standard = standard_docs[i]
        #fetch entities as tuples for value comparison
        predicted_ents = [(entity.start,entity.end, entity.text) for entity in predicted.ents]
        standard_ents = [(entity.start,entity.end, entity.text) for entity in standard.ents]

        #tp = in predicted and in standard (P ^ S)
        tp = len(set(predicted_ents).intersection(standard_ents))
        #fp = in predicted and not in standard (P - S)
        fp = len(set(predicted_ents).difference(standard_ents))
        #fn = in standard and not in predicted (S - P)
        fn = len(set(standard_ents).difference(predicted_ents))

        # skip document if tp and (fp or fn) are equal = 0 (division by 0) 
        if(tp == 0 and (fp == 0 or fn == 0)):
            continue

        precision = tp / (tp + fp)
        recall = tp / (tp + fn)

        
        f1 = 2 * precision * recall / (precision + recall) if (precision * recall) !=0 else 0

        total_tp += tp
        total_fp += fp
        total_fn += fn

        macro_precision += precision
        macro_recall += recall
        macro_f1 += f1

    micro_precision = total_tp / (total_tp + total_fp)
    micro_recall = total_tp / (total_tp + total_fn)
    micro_f1 = 2 * micro_precision * micro_recall / (micro_precision + micro_recall)

    macro_precision /= docs_num
    macro_recall /= docs_num
    macro_f1 /= docs_num

    return {
            "micro": {"f1":micro_f1, "precision":micro_precision, "recall":micro_recall},
            "macro": {"f1":macro_f1, "precision":macro_precision, "recall":macro_recall} 
        }

def ConsistencyResults(dataset_path):
    dataset_path = Path(dataset_path)
    if not dataset_path.exists():
        print(f"Dataset [{dataset_path}] does not exist.")
        raise FileNotFoundError
    
    dataset_name = dataset_path.stem
    with open(dataset_path,"r+") as f:
        spacy_dataset = json.load(f)

    folder_path = Path(".") / "data" #Path(".") / "dockerize" / "containers_data" / "spacy"
    models_path = folder_path / "models" / dataset_name
    models_scores = []
    for i in tqdm(range(len(spacy_dataset)), desc="models"):
        test_set = spacy_dataset[i]
        predicted_docs = []
        standard_docs = []
        nlp = spacy.load(models_path / f"output_{i}" / "model-best" )
        for document in tqdm(test_set, desc="documents"):
            predicted = nlp(document["text"])
            standard = to_docbin(document,nlp)
            predicted_docs.append(predicted)
            standard_docs.append(standard)
        score = measure_scores_strict(predicted_docs, standard_docs)
        models_scores.append(score)

    result = {
        "micro_f1_stdev" : stdev([score["micro"]["f1"] for score in models_scores]),
        "micro_precision_stdev" :stdev([score["micro"]["precision"] for score in models_scores]),
        "micro_recall_stdev" : stdev([score["micro"]["recall"] for score in models_scores]),

        "macro_f1_stdev" : stdev([score["macro"]["f1"] for score in models_scores]),
        "macro_precision_stdev" : stdev([score["macro"]["precision"] for score in models_scores]),
        "macro_recall_stdev" : stdev([score["macro"]["recall"] for score in models_scores])
    }
    return result