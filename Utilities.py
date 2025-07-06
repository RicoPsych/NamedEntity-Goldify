import time
import requests
import json
from pathlib import Path


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


def retry_post(url, params):
    tries = 5
    while tries > 0:
        try:
            rq = requests.post(url=url, params=params)
            return rq
        except requests.ConnectionError:
            tries -= 1
            time.sleep(3)
    if tries <= 0:
        raise ConnectionRefusedError("Could not connect to container")
    
    