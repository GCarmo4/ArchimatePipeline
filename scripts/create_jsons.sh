#!/bin/bash

mkdir Jsons
python actorParse.py
python coordinatorParse.py
python parseProcesses.py
python employeesParse.py
python nodes_to_actors.py
