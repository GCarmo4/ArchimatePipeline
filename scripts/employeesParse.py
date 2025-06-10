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
    column5 = df['ID de sistema']
    column6 = df['ÁrRH']
    column7 = df['Área de recursos humanos']
    column8 = df['Subárea']
    column9 = df['Subárea de recursos humanos']
    column10 = df['Grupo de empregados']
    column11 = df['Subgrupo de empregados']
    column12 = df['Área de processamento da folha']
    column14 = df['Centro de custo']

    return column1, column2, column3, column4, column5, column6, column7, column8, column9, column10, column11, column12, column14

def main():
    unit_found_flag = False
    nodes = readCurrentNodes()
    relations = readCurrentRelations()
    excel_file = openExcelFile('../DataSources/it01_activos_10jan2025.xlsx')
    nomes, centro_de_custo, cargos, area, istid, arRH, area_rh, subarea, subarea_rh, grupo_empregados, subgrupo_empregados, area_folha, centro_custo_nome = extractColumns(excel_file)

    for i in range(len(nomes)):
        
        node_actor = Node(nomes[i], "business-actor")

        node_actor.add_properties("istID", istid[i].lower())
        node_actor.add_properties("type", "employee")
        node_actor.add_properties("Centro cst", centro_de_custo[i])
        node_actor.add_properties("Cargo", cargos[i])
        node_actor.add_properties("ÁrRH", arRH[i])
        node_actor.add_properties("Área de recursos humanos", area_rh[i])
        node_actor.add_properties("Subárea", subarea[i])
        node_actor.add_properties("Subárea de recursos humanos", subarea_rh[i])
        node_actor.add_properties("Grupo de empregados", grupo_empregados[i])
        node_actor.add_properties("Subgrupo de empregados", subgrupo_empregados[i])
        node_actor.add_properties("Área de processamento da folha", area_folha[i])
        node_actor.add_properties("Centro de custo", centro_custo_nome[i])

        nodes[nomes[i]+":business-actor"] = node_actor.to_dict()

        for node_name in nodes:
            for prop in nodes[node_name]["properties"]:
                #print(prop["name"] == "centro de custo")
                #print(prop["value"])
                #print(centro_de_custo[i][2:])
                if prop["name"] == "centro de custo" and prop["value"] == centro_de_custo[i][2:]:
                    #print(centro_de_custo[i][2:])
                    unidade = node_name.split(":")[0]
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