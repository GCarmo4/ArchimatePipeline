# import the connect method
import pymysql
import json
from Node import *
import re
 
# define a connection object

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
    cursor.execute("select distinct BPMNFileName from element;")
    results1 = cursor.fetchall()

    for name in results1:
        file = name[0].split("/")[-1]
        process = file.split(".")[0].split("-")[0]
        print(process)
        if process not in nodes:
            node_process = Node(process, 'business-process')

        cursor.execute("select distinct NameElement from element where TypeElement = 'org.omg.spec.bpmn._20100524.model.TLane' and BPMNFileName = '" + name[0] + "';")
        results_process = cursor.fetchall()

        count = 0
        for row in results_process:
            if row[0] != '' and row[0] in nodes:
                relation_dict_process = {'parent': row[0], 'child': process, 'relation': 'assignment-relationship'}
                count += 1

                if relation_dict_process not in relations:
                    relations.append(relation_dict_process)
        if count != 0:  
            nodes[node_process.name] = node_process.to_dict()
            
            cursor.execute("select distinct ExtensionElement from element where BPMNFileName = '" + name[0] + "';")
            results_application = cursor.fetchall()
            for row in results_application:
                if row[0] != '':
                    matches = re.search(r'name="([^"]+)"[:\s]+value="([^"]+)"', row[0])
                    name = matches.group(1)
                    value = matches.group(2)
                    if name == "system":
                        if value not in nodes:
                            node_application = Node(value, 'application-component')
                            print(node_application.to_dict())
                            nodes[value] = node_application.to_dict()

                        relation_dict_application = {'parent': value, 'child': process, 'relation': 'serving-relationship'}

                        if relation_dict_application not in relations:
                            relations.append(relation_dict_application)

    cursor.close()
    conn.close()

    write_to_json(nodes, 'Jsons/nodes.json')
    write_to_json(relations, 'Jsons/relations.json')

if __name__ == "__main__":
    main()