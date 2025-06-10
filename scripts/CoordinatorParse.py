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
    column1 = df['Unidade']
    column2 = df['Cargo']
    column3 = df['User']
    return column1, column2, column3

def extractUnitCC(df):
    units = []
    cc = []
    for i in range(len(df.columns)):
        if i%2 == 0:
            units += df[df.columns[i]].tolist()
        else:
            cc += df[df.columns[i]].tolist()
    return units, cc

def extractIDNames(df):
    names = df['Nome completo']
    ids = df['ID de sistema']
    idNameMap = {}
    for i in range(len(names)):
        idNameMap[ids[i]] = names[i]
    return idNameMap

def checkParentManager(node_name, nodes, unidades, responsaveis_num):
    try:
        index = unidades.index(nodes[node_name]["parents"][0])
    except:
        return ""
    if responsaveis_num[index] == "":
        return checkParentManager(nodes[node_name]["parents"][0], nodes, unidades, responsaveis_num)
    else:
        return index

def main():
    discrepencies = []
    error = 0
    nodes = readCurrentNodes()
    relations = readCurrentRelations()
    excel_file = openExcelFile('../DataSources/delegacao_de_competencias.xlsx')

    idNameMap = extractIDNames(openExcelFile('../DataSources/it01_activos_10jan2025.xlsx'))

    unidade, cargos, responsavel_num = extractColumns(excel_file)
    responsaveis_num = []
    responsaveis_nome = []
    unidade = unidade.tolist()
    nome = ""

    units, cc = extractUnitCC(openExcelFile('../DataSources/unitCostCenters.xlsx'))

    #definir centros de custo para cada unidade
    for i in range(len(units)):
        if str(units[i]) + ":business-actor" in nodes:
            nodes[units[i] + ":business-actor"].add_properties("centro de custo", cc[i])

    for i in range(len(unidade)):
         
        if unidade[i]+":business-actor" not in nodes:
            discrepencies.append(unidade[i])
            error = 1
        
        if error != 1:

            
            num = responsavel_num[i]
            if num.upper() in idNameMap:
                nome = idNameMap[num.upper()]
            else:
                continue
            if nome == "":    # check if unit has managaer assigned
                # get the manager from the first parent unit that has a manager
                index = checkParentManager(unidade[i], nodes, unidade, responsavel_num)
                if index != "":
                    num = responsavel_num[index]
                    nome = idNameMap[num.upper()]

            else:
                responsaveis_nome = nome.split(", ")
                responsaveis_num = num.split(", ")

            for j in range(len(responsaveis_nome)):
                nodeName = responsaveis_nome[j] + ":business-actor"
                if nodeName not in nodes and error == 0 and nome != "":
                    node_actor = Node(responsaveis_nome[j], "business-actor")    # Create a new node for the manager
                    node_actor.add_properties("istID", responsaveis_num[j])
                    node_actor.add_properties("type", "employee")
                    nodes[nodeName] = node_actor.to_dict()
                if cargos[i] != "":
                    role_name = cargos[i] + " - " + unidade[i]   # Create a name for the managing role
                    node_role = Node(role_name, "business-role")   # Create a new node for the managing role
                    nodes[role_name + ":business-actor"] = node_role.to_dict()

                    relation_dict_actor = {'parent': responsaveis_nome[j], 'child': role_name, 'relation': 'assignment-relationship'}
                    relation_dict_role = {'parent': role_name, 'child': unidade[i], 'relation': 'association-relationship'}
                    relation_dict_unit = {'parent': unidade[i], 'child': responsaveis_nome[j], 'relation': 'composition-relationship'}


                    if relation_dict_actor not in relations:
                        relations.append(relation_dict_actor)

                    if relation_dict_role not in relations:
                        relations.append(relation_dict_role)

                    if relation_dict_unit not in relations:
                        relations.append(relation_dict_unit)

        error = 0
    
    
    write_to_json(nodes, 'Jsons/nodes.json')
    write_to_json(relations, 'Jsons/relations.json')
    #print(discrepencies)
    


if __name__ == "__main__":
    main()
