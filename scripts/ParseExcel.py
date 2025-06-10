import pymysql
import json
from Node import *
import re
import pandas as pd

def readCurrentRelations():
    with open('Jsons/relations.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def readCurrentNodes():
    with open('Jsons/nodes.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def write_to_json(data, file_name):
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def main():
    nodes = readCurrentNodes()
    relations = readCurrentRelations()

    conn = pymysql.connect(
        user='BPMNuser',
        password='BPMNpass',   # Replace with your actual password
        host='localhost',           # Corrected host
        port=3306,                  # Corrected port
        database='BPMNManager'    # Replace with your actual database name
    )
    cursor = conn.cursor()