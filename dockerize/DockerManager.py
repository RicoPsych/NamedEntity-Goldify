import time
import docker
import docker.errors
import json

from Utilities import Singleton

class DockerManager(metaclass=Singleton):
    client:docker.DockerClient
    available_containers: list[str]
    global_config: dict

    def __init__(self, url = None, config_path = './dockerize/containerConfig.json'):
        if url == None:
            print("Connected with local docker instance")
            self.client = docker.from_env()
        else:
            print(f"Connected with docker@{url}")
            self.client = docker.DockerClient(base_url = url)

        with open(config_path, 'r') as file:
            self.global_config = json.load(file)
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


    def start_container(self, config_name):
        config = self.global_config[config_name]

        container_name = config["container_name"]
        image_name = config["image_name"]
        docker_file_path = config["dockerfile"] 
        ports = config["ports"]
        container_port = ports[0][0]
        host_port = ports[0][1]

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

            container = self.client.containers.run(image=img, name=container_name, ports = {f'{container_port}/tcp':host_port}, detach=True)
        #time.sleep(3)
        print(f"Started: {container_name}")
        return container

    def stop_container(self, config_name):
        container_name = self.global_config[config_name]["container_name"]
        container = self.client.containers.get(container_name)
        container.stop()
        print(f"Stopped: {container_name}")

    def get_available_containers(self):
        return self.available_containers

