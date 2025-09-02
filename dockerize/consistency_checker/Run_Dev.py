import json
from pathlib import Path

from ConsistencyResults import ConsistencyResults
from SerializeToDocBin import SerializeToDocBin
from Train import Train

#to use properly move working directory to the consistency_checker folder
print("DEV RUN")

file_name = "categorizedVoxEL_spacy.json"
dataset_path = Path("..") / "containers_data/spacy/datasets" / file_name

dataset_name = dataset_path.stem
results_path = Path(".") / "data/results" / f"{dataset_name.removesuffix("_spacy")}_results.json"

print(dataset_path.resolve().absolute())
print(results_path.resolve().absolute())

SerializeToDocBin(dataset_path)
Train(dataset_path)
results = ConsistencyResults(dataset_path)
print(results)

#with open(results_path,"w+") as f:
#    f.write(json.dumps(results))
