import json
import subprocess
import sys
from typing import Literal
import spacy
from tqdm import tqdm
from pathlib import Path

def Train(dataset_path, lang:Literal["en","fr","es","de"] = "en"):
    dataset_path = Path(dataset_path)
    if not dataset_path.exists():
        print(f"Dataset [{dataset_path}] does not exist.")
        raise FileNotFoundError
    dataset_name = dataset_path.stem

    spacy_model_names = {
        "en" : "en_core_web_trf", #"en_core_web_lg"
        "fr" : "fr_dep_news_trf",
        "es" : "es_dep_news_trf",
        "de" : "de_dep_news_trf",
    }
    try:
        spacy_model_name = spacy_model_names[lang]
        spacy_model = spacy.load(spacy_model_name)
        print(f"{spacy_model_name} already downloaded.")
    except OSError:
        subprocess.run(["python", "-m", "spacy", "download", spacy_model_name])

    with open(dataset_path,"r+") as f:
        spacy_dataset = json.load(f)

    folder_path = Path(".") / "data" #Path(".") / "dockerize" / "containers_data" / "spacy" 
    base_config = Path(".") / f"base_config_{lang}.cfg"
    config = Path(".") / "config.cfg"

    #docbins and models in container?
    doc_path = folder_path / "docbins" / dataset_name
    output_models_path = folder_path / "models" / dataset_name

    model_id = 0

    if output_models_path.exists():
        print(f"Some Models for this dataset already exist. [Remove folder {output_models_path} to retrain models]")
        for i in range(len(spacy_dataset)):
            output_model_path = output_models_path / f"output_{i}"
            if not output_model_path.exists():
                print(f"Starting training from model [{model_id}]")
                break
            model_id += 1

    if model_id == len(spacy_dataset):
        print(f"All models already exist. Skipping Training.")
    else:
        output_models_path.mkdir(exist_ok=True)        
        subprocess.run(["python", "-m", "spacy", "init", "fill-config", base_config, config]) 
        for i in tqdm(range(model_id, len(spacy_dataset)), desc="models"):
            train_doc = doc_path / f"train_{i}.spacy"
            validation_doc = doc_path / f"validation_{i}.spacy"
            output_model_path = output_models_path / f"output_{i}"
            subprocess.run(["python", "-m", "spacy", "train", config, "--output", output_model_path, "--paths.train" , train_doc, "--paths.dev", validation_doc, "--gpu-id", "0"]) 
            ##--nlp.lang "en"
            ##--components.transformer.model.name "roberta-base" "camembert-base"
            