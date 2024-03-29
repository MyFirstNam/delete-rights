from treelib import Tree, Node
# def gen_tree_json(dataTransferPath: list, root: str):
#     """
#     根据传入的，list以及根节点，生成相应的 json
#     @param path:
#     @param root:
#     @return:
#     """
#     node_list = [(i['to'], i['from']) for i in dataTransferPath]
#     tree = Tree()
#     tree.create_node(identifier=root)  # 根节点
#     while len(node_list) != 0:
#         list_identifier = [i.identifier for i in tree.all_nodes()]
#         for node in node_list:
#             if node[1] in list_identifier:
#                 tree.create_node(identifier=node[0], parent=node[1])
#                 node_list.remove(node)
#     return tree.to_json()

from collections import defaultdict
from treelib import Tree
from Json2Tree import json2tree


def build_graph(dataTransferPath):
    graph = defaultdict(list)
    for edge in dataTransferPath:
        graph[edge['from']].append(edge['to'])
        graph[edge['to']].append(edge['from'])
    return graph


def dfs_tree(graph, current_node, visited, tree):
    visited.add(current_node)
    for neighbor in graph[current_node]:
        if neighbor not in visited:
            tree.create_node(identifier=neighbor, parent=current_node)
            dfs_tree(graph, neighbor, visited, tree)


def gen_tree_json(dataTransferPath, root):
    graph = build_graph(dataTransferPath)

    tree = Tree()
    tree.create_node(identifier=root)  # 根节点

    visited_nodes = set()
    dfs_tree(graph, root, visited_nodes, tree)

    return tree.to_json()
