# import the connect method
import pymysql
import json
from Node import *
import re
import pandas as pd
 
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

def openExcelFileFormMembers(file_path):
    df = pd.read_excel(file_path, na_filter = False, sheet_name = "Form Queue Members")
    return df

def openExcelFileFormQueues(file_path):
    df = pd.read_excel(file_path, na_filter = False, sheet_name = "Form Queues")
    df.dropna(inplace=True)
    return df

def openExcelFileFlowMembers(file_path):
    df = pd.read_excel(file_path, na_filter = False, sheet_name = "Flow Queue Members")
    return df

def extractQueuePeopleMap(dfFlow, dfForm):
    form_queue = dfForm["Queue"]
    form_members = dfForm["Member"]

    flow_queue = dfFlow["Flow Queue"]
    flow_members = dfFlow["Member"]

    queue_people_map = {}
    for i in range(len(form_queue)):
        if form_queue[i] not in queue_people_map:
            queue_people_map[form_queue[i]] = [form_members[i]]
        else:
            queue_people_map[form_queue[i]].append(form_members[i])
    
    for i in range(len(flow_queue)):
        if flow_queue[i] not in queue_people_map:
            queue_people_map[flow_queue[i]] = [flow_members[i]]
        else:
            queue_people_map[flow_queue[i]].append(flow_members[i])

    return queue_people_map

def extractQueueHierarchyMap(dfForm):
    form_queue = dfForm["Queue"]
    form_parent = dfForm["Parent Queue"]

    queue_hierarchy_map = {}
    for i in range(len(form_queue)):
        if form_parent[i] != "":
            if form_queue[i] not in queue_hierarchy_map:
                queue_hierarchy_map[form_queue[i]] = [form_parent[i]]
            else:
                queue_hierarchy_map[form_queue[i]].append(form_parent[i])

    return queue_hierarchy_map

def getNameByISTID(istid, nodes):
    for node_name in nodes:
        for prop in nodes[node_name]["properties"]:
            if prop["name"] == "istID" and prop["value"] == istid:
                return node_name.split(":")[0]

    return False

def getProcesses(cursor):
    cursor.execute("SELECT DISTINCT ProcessName FROM BPMNManager.Lane;")
    results1 = cursor.fetchall()
    processes = []

    for result in results1:
        if ".bpmn" in result[0]:
            file = result[0].split("/")[-1]
            split_file = file.split(".")[0].split("-")
            for i in range(len(split_file)-1):
                if i == 0:
                    process = split_file[i]
                else:
                    process += "-" + split_file[i]
                
        else:
            process = result[0]

        if process not in processes:
            processes.append(process)

    return processes

def getSubprocesses(cursor):
    cursor.execute("SELECT ProcessName, ParentProcess FROM BPMNManager.SubProcess;")
    results1 = cursor.fetchall()
    subProcesses = {}

    for result in results1:
        if ".bpmn" in result[1]:
            file = result[1].split("/")[-1]
            split_file = file.split(".")[0].split("-")
            for i in range(len(split_file)-1):
                if i == 0:
                    process = split_file[i]
                else:
                    process += "-" + split_file[i]
                
        else:
            process = result[1]

        subProcess = result[0]

        if process not in subProcesses:
            subProcesses[process] = [subProcess]
        else:
            subProcesses[process].append(subProcess)

    return subProcesses

def getProcessRoles(cursor):
    cursor.execute("SELECT L.NameLane, L.ProcessName FROM BPMNManager.Lane L;")
    results1 = cursor.fetchall()
    rolesProcess = {}
    for result in results1:
        if ".bpmn" in result[1]:
            file = result[1].split("/")[-1]
            split_file = file.split(".")[0].split("-")
            for i in range(len(split_file)-1):
                if i == 0:
                    process = split_file[i]
                else:
                    process += "-" + split_file[i]
                
        else:
            process = result[1]

        if process not in rolesProcess:
            rolesProcess[process] = [result[0]]
        else:
            rolesProcess[process].append(result[0])

    return rolesProcess

def getSubProcessRoles(cursor, subProcesses):
    cursor.execute("SELECT DISTINCT L.NameLane, S.ProcessName FROM BPMNManager.Lane L JOIN BPMNManager.FlowElement F ON L.Reference = F.SourceRef JOIN BPMNManager.SubProcess S on F.NameFlowElement = S.ProcessName;")
    results1 = cursor.fetchall()
    rolesProcess = {}
    for result in results1:
        if result[1] not in rolesProcess:
            rolesProcess[result[1]] = [result[0]]
        else:
            rolesProcess[result[1]].append(result[0])
        if result[1] in subProcesses:
            for subProcess in subProcesses[result[1]]:
                if subProcess not in rolesProcess:
                    rolesProcess[subProcess] = [result[0]]
                else:
                    rolesProcess[subProcess].append(result[0])

    return rolesProcess

def getProcessBObjects(cursor):
    cursor.execute("SELECT DISTINCT F.ProcessName, D.NameDataObject FROM BPMNManager.FlowElement F JOIN BPMNManager.DataObjects D ON F.DataObjectRef = D.DOReference;")
    results1 = cursor.fetchall()
    processBObjects = {}
    for result in results1:
        if ".bpmn" in result[0]:
            file = result[0].split("/")[-1]
            split_file = file.split(".")[0].split("-")
            for i in range(len(split_file)-1):
                if i == 0:
                    process = split_file[i]
                else:
                    process += "-" + split_file[i]
                
        else:
            process = result[0]

        if process not in processBObjects:
            processBObjects[process] = [result[1]]
        else:
            processBObjects[process].append(result[1])

    return processBObjects

def getProcessApps(cursor):
    cursor.execute("SELECT DISTINCT F.ProcessName, E.ExtensionElementContent FROM FlowElement F JOIN ExtensionElements E ON F.SourceRef = E.AssociatedElement;")
    results1 = cursor.fetchall()
    processApps = {}
    for result in results1:
        if ".bpmn" in result[0]:
            file = result[0].split("/")[-1]
            split_file = file.split(".")[0].split("-")
            for i in range(len(split_file)-1):
                if i == 0:
                    process = split_file[i]
                else:
                    process += "-" + split_file[i]
                
        else:
            process = result[0]

        matches = re.search(r'name="([^"]+)"[:\s]+value="([^"]+)"', result[1])
        name = matches.group(1)
        value = matches.group(2)

        if name == "system":
            if process not in processApps:
                processApps[process] = [value]
            else:
                processApps[process].append(value)

    return processApps

def getRoleBObjects(cursor, subProcessRoles):
    cursor.execute("SELECT DISTINCT L.NameLane, D.NameDataObject FROM BPMNManager.Lane L JOIN BPMNManager.FlowElement F ON L.Reference = F.SourceRef JOIN BPMNManager.DataObjects D ON F.DataObjectRef = D.DOReference;")
    results1 = cursor.fetchall()
    roleBObjects = {}
    for result in results1:
        if result[0] not in roleBObjects:
            roleBObjects[result[0]] = [result[1]]
        else:
            roleBObjects[result[0]].append(result[1])

    cursor.execute("SELECT DISTINCT F.ProcessName, D.NameDataObject FROM BPMNManager.FlowElement F JOIN BPMNManager.DataObjects D ON F.DataObjectRef = D.DOReference;")
    results2 = cursor.fetchall()
    for result in results2:
        if result[0] in subProcessRoles:
            for role in subProcessRoles[result[0]]:
                if role not in roleBObjects:
                    roleBObjects[role] = [result[1]]
                else:
                    roleBObjects[role].append(result[1])

    return roleBObjects

def getRoleApps(cursor, subProcessRoles):
    cursor.execute("SELECT DISTINCT L.NameLane, E.ExtensionElementContent FROM BPMNManager.Lane L JOIN BPMNManager.ExtensionElements E ON L.Reference = E.AssociatedElement;")
    results1 = cursor.fetchall()
    roleApps = {}
    for result in results1:
        matches = re.search(r'name="([^"]+)"[:\s]+value="([^"]+)"', result[1])
        name = matches.group(1)
        value = matches.group(2)

        if name == "system":
            if result[0] not in roleApps:
                roleApps[result[0]] = [value]
            else:
                roleApps[result[0]].append(value)

    cursor.execute("SELECT DISTINCT F.ProcessName, E.ExtensionElementContent FROM BPMNManager.FlowElement F JOIN BPMNManager.ExtensionElements E ON F.SourceRef = E.AssociatedElement;")
    results2 = cursor.fetchall()
    for result in results2:
        matches = re.search(r'name="([^"]+)"[:\s]+value="([^"]+)"', result[1])
        name = matches.group(1)
        value = matches.group(2)

        if name == "system":
            if result[0] in subProcessRoles:
                for role in subProcessRoles[result[0]]:
                    if role not in roleApps:
                        roleApps[role] = [value]
                    else:
                        roleApps[role].append(value)
    
    return roleApps

def getRoleList(processRoles):
    roleList = []
    for process in processRoles:
        for role in processRoles[process]:
            if role not in roleList:
                roleList.append(role)
    return roleList

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
    
    #cursor.execute("SELECT L.NameLane, L.ProcessName, D.NameDataObject FROM BPMNManager.Lane L JOIN BPMNManager.FlowElement F ON L.Reference = F.SourceRef JOIN BPMNManager.DataObjects D ON F.DataObjectRef = D.DOReference;")

    processed_processes = []
    processed_roles = []
    role_objects = {}
    role_people = extractQueuePeopleMap(openExcelFileFlowMembers('../DataSources/queues.xlsx'), openExcelFileFormMembers('../DataSources/queues.xlsx'))
    role_hierarchy = extractQueueHierarchyMap(openExcelFileFormQueues('../DataSources/queues.xlsx'))
    print("Role People: ", role_people)
    print("Role Hierarchy: ", role_hierarchy)

    temp = False

#    for result in results1:
#        if ".bpmn" in result[1]:
#            file = result[1].split("/")[-1]
#            split_file = file.split(".")[0].split("-")
#            for i in range(len(split_file)-1):
#                if i == 0:
#                    process = split_file[i]
#                else:
#                    process += "-" + split_file[i]
#                
#        else:
#            process = result[1]


    processes = getProcesses(cursor)

    for process in processes:
        if process + ":business-process" not in nodes:
            processed_processes.append(process)
            node_process = Node(process, 'business-process')
            nodes[node_process.name + ":business-process"] = node_process.to_dict()

        #print(processed_processes)

#        if result[0] not in processed_roles and "{" not in result[0]:
#            if result[0] + " : role:business-role" not in nodes:
#                node_actor = Node(result[0] + " : role", 'business-role')
#                nodes[node_actor.name + ":business-role"] = node_actor.to_dict()
#
#                processed_roles.append(result[0])#

#                relation_dict = {'parent': result[0] + " : role", 'child': process, 'relation': 'assignment-relationship'}
#                if relation_dict not in relations:
#                    relations.append(relation_dict)

    subProcesses = getSubprocesses(cursor)
    for process in subProcesses:
        for subProcess in subProcesses[process]:
            if subProcess + ":business-process" not in nodes:
                node_process = Node(subProcess, 'business-process')
                nodes[subProcess + ":business-process"] = node_process.to_dict()

            if process + ":business-process" in nodes:
                relation_dict = {'parent': process, 'child': subProcess, 'relation': 'composition-relationship'}
                if relation_dict not in relations:
                    relations.append(relation_dict)

    rolesProcess = getProcessRoles(cursor)
    subProcessRoles = getSubProcessRoles(cursor, subProcesses)
    rolesProcess.update(subProcessRoles)
    for process in rolesProcess:
        for role in rolesProcess[process]:
            if role + ":role:business-role" not in nodes and "{" not in role: # not considering dynamic roles
                processed_roles.append(role)
                node_role = Node(role+":role", 'business-role')
                nodes[role + ":role:business-role"] = node_role.to_dict()

            if process + ":business-process" in nodes:
                relation_dict = {'parent': role+":role", 'child': process, 'relation': 'assignment-relationship'}
                if relation_dict not in relations:
                    relations.append(relation_dict)

    #subProcessRoles = getSubProcesseRoles(cursor)
    #for subProcess in subProcessRoles:
    #    if subProcessRoles[subProcess] + ":business-role" not in nodes and "{" not in subProcessRoles[subProcess]:
    #        node_role = Node(subProcessRoles[subProcess], 'business-role')
    #        nodes[subProcessRoles[subProcess] + ":business-role"] = node_role.to_dict()

    #    if subProcess + ":business-process" in nodes:
    #        relation_dict = {'parent': subProcessRoles[subProcess], 'child': subProcess, 'relation': 'assignment-relationship'}
    #        if relation_dict not in relations:
    #            relations.append(relation_dict)

    processBObjects = getProcessBObjects(cursor)
    for process in processBObjects:
        if process + ":business-process" in nodes:
            for obj in processBObjects[process]:
                if obj + ":business-object" not in nodes:
                    node_object = Node(obj, 'business-object')
                    nodes[obj + ":business-object"] = node_object.to_dict()

                relation_dict = {'parent': process, 'child': obj, 'relation': 'access-relationship'}
                if relation_dict not in relations:
                    relations.append(relation_dict)

    processApps = getProcessApps(cursor)
    for process in processApps:
        if process + ":business-process" in nodes:
            for app in processApps[process]:
                if app + ":application-component" not in nodes:
                    node_application = Node(app, 'application-component')
                    nodes[app + ":application-component"] = node_application.to_dict()

                relation_dict = {'parent': app, 'child': process, 'relation': 'serving-relationship'}
                if relation_dict not in relations:
                    relations.append(relation_dict)

    roleBObjects = getRoleBObjects(cursor, subProcessRoles)
    roleApps = getRoleApps(cursor, subProcessRoles)
    roleList = getRoleList(rolesProcess)
    employees = []
    for role in roleList:
        #if role in role_hierarchy:
        #    print("Role Hierarchy: ", role_hierarchy[role])
        #    for child in role_hierarchy[role]:
        #        employees += (role_people[child])
        if role in role_people: #antes era um elif
            print("Role People: ", role_people[role])
            if role + ":role:business-role" in nodes:
                employees += role_people[role]
        elif role in role_hierarchy:
            print("Role Hierarchy: ", role_hierarchy[role])
            for parent in role_hierarchy[role]:
                if parent in role_people:
                    employees += role_people[parent]

        if employees != []:
            print("Employees: ", employees)
            for employee in employees:
                employee_name = getNameByISTID(employee, nodes)
                print("Employee: ", employee)
                print("Employee Name: ", employee_name)
                if employee_name != False:
                    relation_dict = {'parent': employee_name, 'child': role+":role", 'relation': 'assignment-relationship'}
                    if relation_dict not in relations:
                        relations.append(relation_dict)
                
                    if role in roleApps:
                        for app in roleApps[role]:
                            relation_dict = {'parent': employee_name, 'child': app, 'relation': 'association-relationship'}
                            if relation_dict not in relations:
                                relations.append(relation_dict)

                    if role in roleBObjects:
                        for obj in roleBObjects[role]:
                            relation_dict = {'parent': employee_name, 'child': obj, 'relation': 'access-relationship'}
                            if relation_dict not in relations:
                                relations.append(relation_dict)
            employees = []
                             
        
    cursor.close()
    conn.close()

    write_to_json(nodes, 'Jsons/nodes.json')
    write_to_json(relations, 'Jsons/relations.json')

if __name__ == "__main__":
    main()