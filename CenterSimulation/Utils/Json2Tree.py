from treelib import Tree
import json
edges = []
def get_edges(treedict, parent=None):
    name = next(iter(treedict.keys()))
    if parent is not None:
        edges.append((parent, name))
    for item in treedict[name]["children"]:
        if isinstance(item, dict):
            get_edges(item, parent=name)
        else:
            edges.append((name, item))

def json2tree(s):
    # Convert JSON tree to a Python dict
    if '{' not in s:
        tree = Tree()
        tree.create_node(identifier=s)
        return tree
    global edges
    edges = []
    data = json.loads(s)
    get_edges(data)

    tree = Tree()
    tree.create_node(identifier=edges[0][0])
    for edge in edges:
        tree.create_node(identifier=edge[1],parent=edge[0])
    return tree

