from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from dockerize.DockerManager import DockerManager
from Utilities import retry_post, download_untar_file

container_data_path = Path("./dockerize/containers_data/") 

#download rel data
rel_data_path = container_data_path / "rel" 
rel_data_path.mkdir(parents=True,exist_ok=True)

rel_files = ["generic","wiki_2019"]
rel_urls = []
rel_file_paths = []
for rel_data_name in rel_files:
    untar_path = rel_data_path / rel_data_name
    if not untar_path.exists():
        rel_file_url = f"http://gem.cs.ru.nl/{rel_data_name}.tar.gz"
        file_path = rel_data_path / f"{rel_data_name}.tar.gz"
        rel_urls.append(rel_file_url)
        rel_file_paths.append(file_path.absolute())

print(rel_urls)
with ThreadPoolExecutor() as executor:
    executor.map(download_untar_file, rel_urls, rel_file_paths)

manager = DockerManager()

try:
    manager.start_container("consistency_checker")
except:
    print("Could not pull consistency_checker")
    manager.build_image("consistency_checker")
    manager.start_container("consistency_checker")

manager.stop_container("consistency_checker")

print(manager.get_available_containers(completeness=True))
rqs = []
#Create containers beforehand, probe them (makes sure they are ready to use), stop the container without removing them  
for container_name in manager.get_available_containers():
    manager.start_container(container_name)
    rq1 = manager.send_request_to_container(container_name, "This is a probing request for the Docker container", 
                                            incremental=False, infinite_retry=True, retry_delay=5)     
    rqs.append(rq1)
    manager.stop_container(container_name)
    
pass