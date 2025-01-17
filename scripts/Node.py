class Node:
    def __init__(self, name, type):
        self.name = name
        self.children = []
        self.parent = []
        self.type = type
        self.properties = []

    def add_child(self, child):
        self.children.append(child)

    def add_parent(self, parent):
        if parent != "root":
            self.parent.append(parent)
    
    def add_properties(self, property_name, property_value):
        self.properties.append({"name": property_name,
                                "value": property_value})

    def to_dict(self):
        return {
            "name": self.name,
            "type": self.type,
            "properties": self.properties
        }