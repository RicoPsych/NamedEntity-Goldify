NamedEntity-Goldify - a tool for assessing the possible quality aspects of Named Entity Datasets.

Requirements: Python 3.12.9, Docker
Before start: 
- (Recommended) Create new virtual environment for the project.
- Download required python packages from "requirements.txt" ```pip install -r requirements.txt ```
- Start DockerEngine.
- Run ```python prepare_system.py``` to prepare the system files for the tool. The script creates some folders, downloads wikipedia files for rel system, pulls and builds required docker images. Since it downloads some large files, it __will take a long__ time. 
- Once the script ends the system should be prepared.

To simply run the tool use the run.py script, to change dataset simply pass the path as a parameter. Remember to use the proper loader for the dataset.

To add new ner systems for Completeness metric, add it to the docker config file. 
