#!/bin/bash

mkdir Jsons
python OrganizationUnitsParse.py
python CoordinatorParse.py
python employeesParse.py
python BusinessProcessParse.py
python SAPWsdlParse.py
#python nodes_to_actors.py
