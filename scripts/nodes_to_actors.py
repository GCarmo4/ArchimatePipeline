import json
from Node import *

def readCurrentNodes():
    with open('Jsons/nodes.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def write_to_json(data, file_name):
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def main():
    nodes = readCurrentNodes()
    actors = []
    for node in nodes:
        actors.append(nodes[node])
    write_to_json(actors, 'Jsons/actors.json')
    
if __name__ == "__main__":
    main()
