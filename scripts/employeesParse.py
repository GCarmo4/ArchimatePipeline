import pandas as pd
import json
from Node import *


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

def openExcelFile(file_path):
    df = pd.read_excel(file_path, na_filter = False)
    return df

def extractColumns(df):
    column1 = df['Nome completo']
    column2 = df['Centro cst']
    column3 = df['Cargo']
    column4 = df['Subárea de recursos humanos']
    return column1, column2, column3, column4

def main():
    unit_found_flag = False
    nodes = readCurrentNodes()
    relations = readCurrentRelations()
    excel_file = openExcelFile('../DataSources/it01_22out2024.xlsx')
    nomes, centro_de_custo, cargos, area = extractColumns(excel_file)

    for i in range(len(nomes)):
        if nomes[i] not in nodes and cargos[i] != '':
            node_actor = Node(nomes[i], "business-actor")
            node_actor.add_properties("istID", "TODO")
            nodes[nomes[i]] = node_actor.to_dict()

        for node_name in nodes:
            for prop in nodes[node_name]["properties"]:
                print(prop["name"] == "centro de custo")
                print(prop["value"])
                print(centro_de_custo[i][2:])
                if prop["name"] == "centro de custo" and prop["value"] == centro_de_custo[i][2:]:
                    print(centro_de_custo[i][2:])
                    unidade = node_name
                    role_name = cargos[i] + " - " + area[i]
                    node_role = Node(role_name, "business-role")
                    nodes[role_name] = node_role.to_dict()

                    relation_dict_actor = {'parent': nomes[i], 'child': role_name, 'relation': 'assignment-relationship'}
                    relation_dict_role = {'parent': role_name, 'child': unidade, 'relation': 'association-relationship'}
                    relation_dict_unit = {'parent': unidade, 'child': nomes[i], 'relation': 'composition-relationship'}
                    if relation_dict_actor not in relations:
                        relations.append(relation_dict_actor)
                    if relation_dict_role not in relations:
                        relations.append(relation_dict_role)
                    if relation_dict_unit not in relations:
                        relations.append(relation_dict_unit)
                    unit_found_flag = True
                    break
            if unit_found_flag:
                unit_found_flag = False
                break


    write_to_json(nodes, 'Jsons/nodes.json')
    write_to_json(relations, 'Jsons/relations.json')

if __name__ == "__main__":
    main()