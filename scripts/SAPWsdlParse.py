import os
import xml.etree.ElementTree as ET
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

def list_files_in_directory(directory):
    """
    Lists the name of every file in the specified directory.

    :param directory: Path to the directory.
    :return: List of file names in the directory.
    """
    try:
        files = [file for file in os.listdir(directory) if os.path.isfile(os.path.join(directory, file))]
        return files
    except FileNotFoundError:
        print(f"Directory not found: {directory}")
        return []
    except PermissionError:
        print(f"Permission denied to access: {directory}")
        return []

def get_service_name(xml_file):
    """
    Extracts the name from the service field in the XML file.

    :param xml_file: Path to the XML file.
    :return: The name value if found, else None.
    """
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Find the service tag and get the name attribute
        service = root.find(".//wsdl:service", namespaces={"wsdl": "http://schemas.xmlsoap.org/wsdl/"})

        if service is not None and 'name' in service.attrib:
            return service.attrib['name']
        else:
            print("Service tag or name attribute not found in the XML file.")
            return None

    except ET.ParseError as e:
        print(f"Error parsing the XML file: {e}")
        return None
    except FileNotFoundError:
        print(f"File not found: {xml_file}")
        return None

# Example usage
if __name__ == "__main__":
    nodes = readCurrentNodes()
    relations = readCurrentRelations()
    directory_path = "../DataSources/interfaces"  # Replace with your directory path

    files = list_files_in_directory(directory_path)
    if files:
        print("Files in directory:")
        for file in files:
            print(file)
    else:
        print("No files found in the directory or unable to access.")

    # Extract service name from the given XML file
    xml_file_path = "../DataSources/interfaces/BN__ZISTWS_DADOS_PICAGEM.xml"  # Replace with your XML file path
    service_name = get_service_name(xml_file_path)
    if service_name:
        print(f"Service name: {service_name}")

    if "SAP" not in nodes:
        print("SAP node not found in the nodes.")
        exit(1)
    
    if (service_name + ":application-interface") not in nodes:
        node_interface = Node(service_name, "application-interface")
        nodes[service_name + ":application-interface"] = node_interface.to_dict()

    if (service_name + ":application-service") not in nodes:
        node_service = Node(service_name, "application-service")
        nodes[service_name + ":application-service"] = node_service.to_dict()

    relation_dict_interface = {'parent': "SAP", 'child': service_name, 'relation': 'composition-relationship'}
    relation_dict_service = {'parent': service_name, 'child': service_name, 'relation': 'assignment-relationship'}

    if relation_dict_interface not in relations:
        relations.append(relation_dict_interface)
    
    if relation_dict_service not in relations:
        relations.append(relation_dict_service)

    write_to_json(nodes, 'Jsons/nodes.json')
    write_to_json(relations, 'Jsons/relations.json')


