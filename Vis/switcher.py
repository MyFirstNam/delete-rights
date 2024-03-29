import json
from copy import deepcopy

# 原始 JSON 数据
data = {"b1000": {"children": [{"b1001": {"children": ["b1002"]}}, {"b1003": {"children": ["b1004"]}}]}}


def parse_tree(parent, tree):
    nodes = []
    links = []

    def generate_edge_id(target_node_id):
        # 生成边的唯一标识符，格式为 "edge-${target_node_id}"
        return f"edge-{target_node_id}"

    def parse_recursive(parent, tree):
        for key, value in tree.items():
            # 添加节点
            if key not in [node['id'] for node in nodes]:
                nodes.append({"id": key})

            # 添加与父节点的边，为边生成特定格式的标识符
            if parent is not None:
                edge_id = generate_edge_id(key)
                links.append({"source": parent, "target": key, "id": edge_id})

            # 递归处理子节点
            if isinstance(value, dict) and 'children' in value:
                for child in value['children']:
                    if isinstance(child, dict):
                        parse_recursive(key, child)
                    else:
                        if child not in [node['id'] for node in nodes]:
                            nodes.append({"id": child})
                        edge_id = generate_edge_id(child)
                        links.append({"source": key, "target": child, "id": edge_id})

    # 调用递归函数开始解析
    parse_recursive(parent, tree)

    # 返回结果
    return nodes, links


if __name__ == '__main__':
    # 解析数据
    nodes, links = parse_tree(None, data)

    # 转换为 JSON
    graph_json = json.dumps({"nodes": nodes, "links": links})
    print(graph_json)
