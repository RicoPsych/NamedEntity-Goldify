import re
import time
import requests
import json
import tarfile
from pathlib import Path

from tqdm import tqdm


def SaveResult(result, results_path, filename):
    json_result = json.dumps(result)
    # Writing to sample.json

    Path(results_path).mkdir(parents=True, exist_ok=True)
    out_path = Path(results_path) / f"{filename}.json"

    with open(out_path, "w") as file:
        file.write(json_result)

def SaveTable(table, path, filename):
    Path(path).mkdir(parents=True, exist_ok=True)
    out_path = Path(path) / f"{filename}.tex"

    with open(out_path, "w") as file:
        file.write(table)


class Singleton(type):
    _instances = {}
    def __call__(self, *args, **kwds):
        if self not in self._instances:
            instance = super().__call__(*args, **kwds)
            self._instances[self] = instance
        return self._instances[self]

def retry_get(url, params = None, data = None, json=None, headers = None, tries = 10, sleep_time = 3, incremental = False, infinite_retry = False):
    #sleep_time * 2^(trynum - 1) 
    #default 3 , 6, 12 , 24, 48, 96 ...
    while tries > 0 or infinite_retry:
        try:
            rq = requests.get(url=url, data=data, json=json, params=params, headers=headers)
            return rq
        except requests.ConnectionError:
            tries -= 1
            tqdm.write(f"Connection Error [{url}]. Next try in {sleep_time}s [remaining tries {"infinite" if infinite_retry else tries}]")        
            time.sleep(sleep_time)
            if incremental:
                sleep_time += sleep_time
    if tries <= 0:
        raise ConnectionRefusedError("Could not connect to container")
    

def retry_post(url, params = None, data = None, json=None, headers = None, tries = 10, sleep_time = 3, incremental = False, infinite_retry = False):
    #sleep_time * 2^(trynum - 1) 
    #default 3 , 6, 12 , 24, 48, 96 ...
    while tries > 0 or infinite_retry:
        try:
            rq = requests.post(url=url, data=data, json=json, params=params, headers=headers)
            return rq
        except requests.ConnectionError:
            tries -= 1
            tqdm.write(f"Connection Error [{url}]. Next try in {sleep_time}s [remaining tries {"infinite" if infinite_retry else tries}]")        
            time.sleep(sleep_time)
            if incremental:
                sleep_time += sleep_time
    if tries <= 0:
        raise ConnectionRefusedError("Could not connect to container")
    
def download_untar_file(url, target_path):
    target_path = target_path.absolute()
    untar_path = target_path.parent.absolute()
    download_file(url,target_path)
    tqdm.write(f"Extracting {target_path} to {untar_path}.")
    file = tarfile.open(target_path)
    file.extractall(untar_path)

def download_file(url, target_path):
    target_path = target_path.absolute()
    tqdm.write(f"Downloading {url} to {target_path}.")
    with requests.get(url, stream=True) as rq:
        total_size = int(rq.headers.get('content-length'))
        with tqdm(total=total_size, unit="B", unit_scale=True, unit_divisor=1024) as progress_bar:
            with open(target_path, mode="wb") as file: 
                chunk_size = 1024*1024
                for chunk in rq.iter_content(chunk_size=chunk_size):
                    chunk_size = file.write(chunk)
                    progress_bar.update(chunk_size)
    tqdm.write(f"Downloaded {target_path}")

def get_proxy_list():
    response = requests.get("https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=json&anonymity=Anonymous&timeout=20000").json()
    proxies = [{"http":proxy["proxy"],"https":proxy["proxy"]} for proxy in response['proxies']]
    return proxies

def recursive_replace(object_dict, value_to_replace, value):
    for key in object_dict:
        match object_dict[key]:
            case str():
                object_dict[key] = object_dict[key].replace(value_to_replace, value)
            case dict():
                object_dict[key] = recursive_replace(object_dict[key],value_to_replace,value)
    return object_dict


def find_closest_substr(plain_text:str, substr_:str ,index:int):
    #strip from start and end the non alphanumeric characters
    #split on non alphanumeric parts
    #get first alphanumeric part, find with that
    substr = re.sub(r'\A\W+|\W+\Z', '', substr_.lower(), flags=re.I)
    split = re.split('[^a-zA-Z0-9]', substr)
    split = list(filter(lambda part: part != '',split))
    substr = split[0] if len(split) > 0 else substr
    #print(substr)
    if substr == "":
        return -1 #if substr is empty - return -1

    all_occurrences = []
    search_from = 0
    end_id = plain_text.lower().find(substr, index) #find closest after
    if end_id == -1:
        end_id = index

    possible_id = -1
    #for up to closest after or index if none after
    while(possible_id <= end_id):
        possible_id = plain_text.lower().find(substr, search_from)
        if(possible_id == -1):
            break
        all_occurrences.append(possible_id)
        search_from = possible_id + len(substr)

    all_occurrences.sort(key = lambda id: abs(id - index))
    
    return all_occurrences[0] if len(all_occurrences) > 0 else -1