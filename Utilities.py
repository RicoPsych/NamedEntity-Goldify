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
            print(f"Connection Error [{url}]. Next try in {sleep_time}s [remaining tries {"infinite" if infinite_retry else tries}]")        
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
            print(f"Connection Error [{url}]. Next try in {sleep_time}s [remaining tries {"infinite" if infinite_retry else tries}]")        
            time.sleep(sleep_time)
            if incremental:
                sleep_time += sleep_time
    if tries <= 0:
        raise ConnectionRefusedError("Could not connect to container")
    
def download_untar_file(url, target_path):
    target_path = target_path.absolute()
    untar_path = target_path.parent.absolute()
    download_file(url,target_path)
    print(f"Extracting {target_path} to {untar_path}.")
    file = tarfile.open(target_path)
    file.extractall(untar_path)

def download_file(url, target_path):
    target_path = target_path.absolute()
    print(f"Downloading {url} to {target_path}.")
    with requests.get(url, stream=True) as rq:
        total_size = int(rq.headers.get('content-length'))
        with tqdm(total=total_size, unit="B", unit_scale=True, unit_divisor=1024) as progress_bar:
            with open(target_path, mode="wb") as file: 
                chunk_size = 1024*1024
                for chunk in rq.iter_content(chunk_size=chunk_size):
                    chunk_size = file.write(chunk)
                    progress_bar.update(chunk_size)
    print(f"Downloaded {target_path}")

def get_proxy_list():
    response = requests.get("https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=json&anonymity=Anonymous&timeout=20000").json()
    proxies = [{"http":proxy["proxy"],"https":proxy["proxy"]} for proxy in response['proxies']]
    return proxies

#get_proxy_list()