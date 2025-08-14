from dockerize.DockerManager import DockerManager
from Utilities import retry_post

from models.Dataset import Dataset
from models.Document import Document
from models.Entity import Entity

import json 
import tqdm

def GrammarCorrectness(dataset, language = "auto"):
    if isinstance(dataset,Dataset):
        documents = dataset.documents
    elif isinstance(dataset,list) and isinstance(dataset[0],Document):
        documents = dataset
    elif isinstance(dataset,Document):
        documents = [dataset]
    else:
        raise "Invalid Input dataset"
    
    manager = DockerManager()
    name = 'languageTool'
    manager.start_container(config_name=name)

    print("Grammar Correctness")

    errors = {}
    errors_sum = 0
    dataset_languages = {}
    for document in tqdm.tqdm(documents):
        # https://languagetool.org/http-api/swagger-ui/#!/default/post_check
        params = {
            "text": document.plain_text,
            "language": language            
        }

        rq = retry_post("http://localhost:8010/v2/check", params=params)
        response = json.loads(rq.text)
        detected_language = response["language"]["name"]
        dataset_languages[detected_language] = dataset_languages.get(detected_language,0) + 1
        
        errors_num = len(response["matches"])
        errors_sum += errors_num
        errors[document.name] = errors_num

    manager.stop_container(config_name=name)

    errors_mean = errors_sum/len(documents)

    print("Done")
    return {
        "errors_sum":errors_sum,
        "errors_mean":errors_mean,
        "errors_per_document":errors,
        "text_languages": dataset_languages,

    }

# docker pull erikvl87/languagetool
# docker run --rm -p 8010:8010 erikvl87/languagetool