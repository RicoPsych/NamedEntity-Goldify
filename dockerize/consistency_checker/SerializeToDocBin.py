import json
import sys
import subprocess

import spacy
from spacy.tokens import DocBin
from tqdm import tqdm
from spacy.util import filter_spans
from pathlib import Path

def transform_and_save_set(dataset, doc_path):
    nlp = spacy.blank('en')
    doc_bin = DocBin()
    for training_example in tqdm(dataset, desc="documents"):
        text = training_example['text']
        labels = training_example['entities']

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
        doc_bin.add(doc)
    doc_bin.to_disk( doc_path )

def SerializeToDocBin(dataset_path):
    dataset_path = Path(dataset_path)
    if not dataset_path.exists():
        print(f"Dataset [{dataset_path}] does not exist.")
        raise FileNotFoundError
    dataset_name = dataset_path.stem

    #/ "dockerize" / "containers_data" / "spacy" / 
    docbin_folder_path = Path(".")/ "data" / "docbins" / dataset_name
    if docbin_folder_path.exists():
        print(f"Docbins for this dataset already exist. Skipping serialization. [Remove folder {docbin_folder_path} to serialize this dataset]")
    else:
        docbin_folder_path.mkdir(exist_ok=True)
        with open(dataset_path,"r+") as f:
            spacy_dataset = json.load(f)

        #create 10 training sets
        for i in tqdm(range(len(spacy_dataset)), desc="chunks"):
            test_set = spacy_dataset[i] #choose chunk as test set
            chunk_list = spacy_dataset[:i] + spacy_dataset[i+1:] 
            validation_set = chunk_list[0] #use first chunk as validation
            chunk_list = chunk_list[1:] #and rest as train set
            train_set = [doc for chunk in chunk_list for doc in chunk] 

            #test set?

            doc_train_path = docbin_folder_path / f"train_{i}.spacy"
            transform_and_save_set(train_set, doc_train_path)

            #validation only
            doc_validation_path = docbin_folder_path / f"validation_{i}.spacy"
            transform_and_save_set(validation_set, doc_validation_path)

            # nlp = spacy.blank('en')
            # doc_bin = DocBin()
            # for training_example in tqdm(train_set, desc="documents"):
            #     text = training_example['text']
            #     labels = training_example['entities']

            #     doc = nlp.make_doc(text)
            #     ents = []
            #     for start, end, label in labels: 
            #         span = doc.char_span(start, end, label=label, alignment_mode="contract")
            #         if span is None:
            #             print("Skipping entity")
            #         else:
            #             ents.append(span)
            #     filtered_ents = filter_spans(ents)
            #     doc.ents = filtered_ents
            #     doc_bin.add(doc)

            # doc_path = docbin_folder_path / f"train_{i}.spacy"
            # doc_bin.to_disk( doc_path )
