from fastapi import FastAPI
import json
from pathlib import Path
import sys
from SerializeToDocBin import SerializeToDocBin
from Train import Train
from ConsistencyResults import ConsistencyResults

app = FastAPI()

@app.post("/")
def get_dataset_consistency(file_name, lang):
    dataset_path = Path("/consistency/data/datasets") / file_name
    dataset_name = dataset_path.stem
    results_path = Path("/consistency/data/results") / f"{dataset_name.removesuffix("_spacy")}_results.json"
    
    SerializeToDocBin(dataset_path)
    Train(dataset_path, lang)
    results = ConsistencyResults(dataset_path)
    #print(results)
    with open(results_path,"w+") as f:
        f.write(json.dumps(results))
    return results