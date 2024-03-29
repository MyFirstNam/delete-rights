from collections import defaultdict
from treelib import Tree

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