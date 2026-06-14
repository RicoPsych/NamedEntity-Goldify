NamedEntity-Goldify - a tool for assessing the possible quality aspects of Named Entity Datasets.

Requirements: Python 3.12.9, Docker
Before start: 
- (Recommended) Create new virtual environment for the project.
- Download required python packages from "requirements.txt" ```pip install -r requirements.txt ```
- Start DockerEngine.
- Run ```python prepare_system.py``` to prepare the system files for the tool. The script creates some folders, downloads wikipedia files for rel system, pulls and builds required docker images. Since it downloads some large files, it __will take a long__ time. 
- Once the script ends the system should be prepared.

In run script, make sure to set the path for directory containing the datasets for assessment.
```datasets_dir=r"<desired_dir_path>"```

To simply run the tool use the run.py script, to change dataset simply pass the path as a parameter. Remember to use the proper loader for the dataset.

To add new ner systems for Completeness metric, add it to the docker config file. 


### Update:
Updated and fixed completeness metric integration function which didn't work as intended.
completness_results_recompute.py - script runner to fetch completness data from previous results and recompute with fixed function. 
    pipeline by default uses the same fixed function, so only usable for results computed before the update.