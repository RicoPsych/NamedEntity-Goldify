import copy
import subprocess
import time
import docker
import docker.types
import docker.errors
import json
import urllib.parse

from pathlib import Path

import tqdm

from Utilities import Singleton, retry_get, retry_post, recursive_replace

class DockerManager(metaclass=Singleton):
    client:docker.DockerClient
    available_containers: list[str]
    global_config: dict

    def __init__(self, url = None, config_path = './dockerize/containerConfig.json'):
        tqdm.tqdm.write("Connecting to docker instance...")
        if url == None:
            self.client = docker.from_env()
            tqdm.tqdm.write("Connected with local docker instance")
        else:
            self.client = docker.DockerClient(base_url = url)
            tqdm.tqdm.write(f"Connected with docker@{url}")

        with open(config_path, 'r') as file:
            #change docker config to absolute paths during config loading
            config_str = file.read().replace("$PWD$", str(Path.cwd()).replace("\\","\\\\"))
            self.global_config = json.loads(config_str)
            self.available_containers = list(self.global_config.keys())
            tqdm.tqdm.write(f"Loaded container config form: {config_path}")

    # def initialize(self, url = None, config_path = './docker/containerConfig.json'):
    #     if url == None:
    #         self.client = docker.from_env()
    #     else:
    #         self.client = docker.DockerClient(base_url = url)

    #     with open(config_path, 'r') as file:
    #         self.global_config = json.load(file)
    #         self.available_containers = list(self.global_config.keys())

    def start_container(self, config_name, detach = True, command = None):
        full_container_config = self.global_config[config_name]
        run_config = full_container_config.get("docker", None)
        
        if full_container_config.get("gpu",False) == True:
            run_config["device_requests"]=[docker.types.DeviceRequest(capabilities=[['gpu']],count=-1,driver='nvidia')]

        if run_config is not None:
            container_name = run_config["name"]
            image_name = run_config.get("image","")
            docker_file_path = run_config.get("dockerfile","") 
            #ports = config["ports"]
            #container_port = ports[0][0]
            #host_port = ports[0][1]
            
            try:
                container = self.client.containers.get(container_name)
                container.start()
            except docker.errors.NotFound:
                try:
                    img = self.client.images.get(image_name)
                except docker.errors.ImageNotFound:
                    if docker_file_path != "":
                        tqdm.tqdm.write(f"Building: {container_name}")
                        img = self.client.images.build(path=docker_file_path, tag=image_name)
                    else:
                        tqdm.tqdm.write(f"Pulling: {container_name}")
                        img = self.client.images.pull(image_name)

                #container = self.client.containers.run(image=img, name=container_name, ports = {f'{container_port}/tcp':host_port}, detach=True) --gpus all
                container = self.client.containers.run(**run_config, detach = detach, command = command)
            #time.sleep(3)
            tqdm.tqdm.write(f"Started: {container_name}")
            return container
        else:
            tqdm.tqdm.write(f"Config {config_name} does not have docker container defined.")
            return None

    def stop_container(self, config_name):
        config = self.global_config[config_name].get("docker", None)
        if config is not None:
            container_name = config["name"]
            container = self.client.containers.get(container_name)
            container.stop()
            tqdm.tqdm.write(f"Stopped: {container_name}")
        else:
            tqdm.tqdm.write(f"Config {config_name} does not have docker container defined.")

    def get_available_containers(self, completeness = False):
        if completeness is True:
            #get names of configs for completeness metric, configs with "for_completeness" field
            return [config_name for config_name in self.available_containers if self.global_config[config_name].get("for_completeness", False) ]
        return self.available_containers

    def send_request_to_container(self, config_name, data_list: str | list[str], infinite_retry = False, incremental=True, retry_delay = 3):
        rq_config = self.global_config[config_name].get("request", None) 
        if rq_config is not None:
            rq_config = copy.deepcopy(rq_config) #copy by value
            
            url = rq_config["url"]
            headers = rq_config.get("headers", None)
            params = rq_config.get("params", None)
            json_params = rq_config.get("json_params", None)
            body = rq_config.get("body", None)
            json_body = rq_config.get("json_body", None)
            parse_values = rq_config.get("parse_payload", None) or {}


            if not isinstance(data_list,list):
                data_list = [data_list]

            for i, data in enumerate(data_list):
                parsed_data = data.rstrip() #flair errors out when there are newilines at the end of text
                # parsed_data = data.replace('"','\\"') # " -> \"
                # parsed_data = data.replace("\\\"","\"") # \" -> "
                # parsed_data = parsed_data.replace("\\'","'") # \' -> '
                for key in parse_values: #parse values specific for each rq
                    parsed_data = parsed_data.replace(key,parse_values[key])

                str_to_replace = "$TEXT_DATA$" if len(data_list) == 1 else f"$TEXT_DATA_{i}$"
                url = url.replace(str_to_replace, urllib.parse.quote_plus(parsed_data))
                if params is not None:
                    params = params.replace(str_to_replace, urllib.parse.quote_plus(parsed_data))
                if json_params is not None:
                    json_params = recursive_replace(json_params, str_to_replace, parsed_data)
                if body is not None:
                    parsed_data = urllib.parse.quote_plus(data)
                    body = body.replace(str_to_replace, parsed_data)
                if json_body is not None:
                    parsed_data = data.replace('"','\\"') # " -> \"
                    json_body = recursive_replace(json_body, str_to_replace, parsed_data)
            
            if params is None:
                params = json_params 

            method = rq_config.get("method", "POST")
            if method == "GET":
                return retry_get(url, params = params, data = body, json=json_body, headers = headers, sleep_time = retry_delay, incremental=incremental, infinite_retry=infinite_retry)
            elif method == "POST":
                return retry_post(url, params = params, data = body, json=json_body, headers = headers, sleep_time = retry_delay, incremental=incremental, infinite_retry=infinite_retry)
            else:
                print(f"Config's {config_name} request method undefined.")
                return None
        else:
            print(f"Config {config_name} does not have request defined.")
            return None
        
    def build_image(self, config_name):
        tqdm.tqdm.write(f"Building image for {config_name}")
        build_config = self.global_config[config_name]["build"]
        path = str(Path(build_config["dockerfile"]))
        tag = build_config["tag"]
        subprocess.run(["docker ", "build", "-t", tag, path]) 
        return

        # works weirdly, creates additional containers, does not remove them, blocking method -> streaming logs unavailable
        #_, logs = self.client.images.build(path = path, tag = tag) 
        #for line in logs:
        #    print(line)
