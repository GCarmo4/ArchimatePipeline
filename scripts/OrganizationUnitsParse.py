import json
from Node import *

def parse_hierarchy_from_tsv(file_path):
    root = Node("root", "")  # Dummy root node
    stack = [root]

    with open(file_path, 'r', encoding='utf-8-sig') as file:
        print(file)
        for line in file:
            stripped_line = line.strip()
            if stripped_line == "":
                continue  # Skip empty lines

            line = line.replace("    ", "\t")

            # Count the tabs to determine the level of the node
            level = line.count('\t')
            current_node = Node(stripped_line, "business-actor")

            # Ensure the stack is at the correct level
            while len(stack) > level + 1:
                stack.pop()

            # Add the current node as a child of the last node in the stack
            stack[-1].add_child(current_node)

            # Set the parent of the current node
            current_node.add_parent(stack[-1].name)

            # Push the current node onto the stack
            stack.append(current_node)

    return root

# Traverse the tree, collect actors and relationships
def traverse_and_collect(node, parent=None, relations=[], nodes={}):
    if node.name != "root" and node.to_dict():  # Skip the dummy root node
        nodeName = node.name + ":" + node.type
        if nodeName not in nodes:
            nodes[nodeName] = node.to_dict()

    if parent and node.name != "root" and parent.name != "root":  # Create relationships if there is a parent
        relations.append({"parent": parent.name, "child": node.name, "relation": "composition-relationship"})

    for child in node.children:
        traverse_and_collect(child, node, relations, nodes)

# Write data to JSON file
def write_to_json(data, file_name):
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def main():
    file_path = "../DataSources/units.tsv"

    # Parse the hierarchy from the TSV file
    tree_root = parse_hierarchy_from_tsv(file_path)

    # Collect actors and relationships
    nodes = {}
    relations_list = []
    traverse_and_collect(tree_root, relations=relations_list, nodes=nodes)

    # Write tree to a JSON file
    write_to_json(nodes, 'Jsons/nodes.json')

    # Write relations to a JSON file
    write_to_json(relations_list, 'Jsons/relations.json')

    # Output result for confirmation
    print("Actors and relations have been written to JSON files")
    
if __name__ == "__main__":
    main()
