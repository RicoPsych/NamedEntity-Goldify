import json
import subprocess
import sys
import spacy
from tqdm import tqdm
from pathlib import Path

def Train(dataset_path):
    dataset_path = Path(dataset_path)
    if not dataset_path.exists():
        print(f"Dataset [{dataset_path}] does not exist.")
        raise FileNotFoundError
    dataset_name = dataset_path.stem

    #en_core_web_trf
    spacy_model_name = "en_core_web_lg"
    try:
        spacy_model = spacy.load(spacy_model_name)
        print(f"{spacy_model_name} already downloaded.")
    except OSError:
        subprocess.run(["python", "-m", "spacy", "download", spacy_model_name])

    with open(dataset_path,"r+") as f:
        spacy_dataset = json.load(f)

    folder_path = Path(".") / "data" #Path(".") / "dockerize" / "containers_data" / "spacy" 
    base_config = Path(".") / "base_config.cfg"
    config = Path(".") / "config.cfg"

    #docbins and models in container?
    doc_path = folder_path / "docbins" / dataset_name
    output_models_path = folder_path / "models" / dataset_name

    if output_models_path.exists():
        print(f"Models for this dataset already exist. Skipping training. [Remove folder {output_models_path} to retrain models]")
    else:
        output_models_path.mkdir(exist_ok=True)
        subprocess.run(["python", "-m", "spacy", "init", "fill-config", base_config, config]) #redundant - not needed more than once? if config exists, do not create? (same config for every dataset) 
        for i in tqdm(range(len(spacy_dataset)), desc="models"):
            train_doc = doc_path / f"train_{i}.spacy"
            validation_doc = doc_path / f"validation_{i}.spacy"
            output_model_path = output_models_path / f"output_{i}"
            subprocess.run(["python", "-m", "spacy", "train", config, "--output", output_model_path, "--paths.train" , train_doc, "--paths.dev", validation_doc]) 
