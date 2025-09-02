import subprocess
import time
import docker
import docker.types
import docker.errors
import json
from pathlib import Path

from Utilities import Singleton, retry_get, retry_post

class DockerManager(metaclass=Singleton):
    client:docker.DockerClient
    available_containers: list[str]
    global_config: dict

    def __init__(self, url = None, config_path = './dockerize/containerConfig.json'):
        print("Connecting to docker instance...")
        if url == None:
            self.client = docker.from_env()
            print("Connected with local docker instance")
        else:
            self.client = docker.DockerClient(base_url = url)
            print(f"Connected with docker@{url}")

        with open(config_path, 'r') as file:
            #change docker config to absolute paths during config loading
            config_str = file.read().replace("$PWD$", str(Path.cwd()).replace("\\","\\\\"))
            self.global_config = json.loads(config_str)
            self.available_containers = list(self.global_config.keys())
            print(f"Loaded container config form: {config_path}")

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
                        print(f"Building: {container_name}")
                        img = self.client.images.build(path=docker_file_path, tag=image_name)
                    else:
                        print(f"Pulling: {container_name}")
                        img = self.client.images.pull(image_name)

                #container = self.client.containers.run(image=img, name=container_name, ports = {f'{container_port}/tcp':host_port}, detach=True) --gpus all
                container = self.client.containers.run(**run_config, detach = detach, command = command)
            #time.sleep(3)
            print(f"Started: {container_name}")
            return container
        else:
            print(f"Config {config_name} does not have docker container defined.")
            return None

    def stop_container(self, config_name):
        config = self.global_config[config_name].get("docker", None)
        if config is not None:
            container_name = config["name"]
            container = self.client.containers.get(container_name)
            container.stop()
            print(f"Stopped: {container_name}")
        else:
            print(f"Config {config_name} does not have docker container defined.")

    def get_available_containers(self, completeness = False):
        if completeness is True:
            #get names of configs for completeness metric, configs with "for_completeness" field
            return [config_name for config_name in self.available_containers if self.global_config[config_name].get("for_completeness", False) ]
        return self.available_containers

    def send_request_to_container(self, config_name, data_list: str | list[str], infinite_retry = False, incremental=True, retry_delay = 3):
        rq_config = self.global_config[config_name].get("request", None) 
        if rq_config is not None:
            url = rq_config["url"]
            headers = rq_config.get("headers", None)
            params = rq_config.get("params", None)
            body = rq_config.get("body", None)

            
            if not isinstance(data_list,list):
                data_list = [data_list]

            for i, data in enumerate(data_list):
                parsed_data = data.replace("\"","\\\"")
                str_to_replace = "$TEXT_DATA$" if len(data_list) == 1 else f"$TEXT_DATA_{i}$"
                url = url.replace(str_to_replace, parsed_data)
                if params is not None:
                    params = params.replace(str_to_replace, parsed_data)
                if body is not None:
                    body = body.replace(str_to_replace, parsed_data)
        
            method = rq_config.get("method", "POST")
            if method == "GET":
                return retry_get(url, params = params, data = body, headers = headers, sleep_time = retry_delay, incremental=incremental, infinite_retry=infinite_retry)
            elif method == "POST":
                return retry_post(url, params = params, data = body, headers = headers, sleep_time = retry_delay, incremental=incremental, infinite_retry=infinite_retry)
            else:
                print(f"Config's {config_name} request method undefined.")
                return None
        else:
            print(f"Config {config_name} does not have request defined.")
            return None
        
    def build_image(self, config_name):
        print(f"Building image for {config_name}")
        build_config = self.global_config[config_name]["build"]
        path = str(Path(build_config["dockerfile"]))
        tag = build_config["tag"]
        subprocess.run(["docker ", "build", "-t", tag, path]) 
        return

        # works weirdly, creates additional containers, does not remove them, blocking method -> streaming logs unavailable
        #_, logs = self.client.images.build(path = path, tag = tag) 
        #for line in logs:
        #    print(line)
