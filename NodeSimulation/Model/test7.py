#
#
#
# from treelib import Tree
#
# def get_path_to_node(tree, node_id):
#     """
#     获取从根节点到指定节点的路径（包括这两个节点）。
#     :param tree: Tree对象
#     :param node_id: 目标节点的ID
#     :return: 包含路径上所有节点的列表
#     """
#     path = []
#     current_node_id = node_id
#     while current_node_id:  # 当current_node_id为None时停止循环，这意味着到达了根节点
#         node = tree.get_node(current_node_id)  # 获取当前节点对象
#         if node is None:
#             break  # 如果节点不存在，则退出循环
#         path.append(node)  # 将当前节点添加到路径列表中
#         current_node_id = tree.parent(current_node_id)  # 获取当前节点的父节点ID
#
#     return path[::-1]  # 返回反转的路径列表，以使其从根节点开始
#
# # 示例使用
# tree = Tree()
# tree.create_node("Root", "root")  # 根节点
# tree.create_node("Child 1", "child1", parent="root")
# tree.create_node("Child 2", "child2", parent="child1")  # 添加更深层的子节点
#
# path = get_path_to_node(tree, "child2")  # 获取从根节点到"child2"的路径
# for node in path:
#     print(node.tag)  # 打印路径上每个节点的标签






from treelib import Tree

def get_path_to_node(tree, node_id):
    """
    获取从根节点到指定节点的路径（包括这两个节点）。
    :param tree: Tree对象
    :param node_id: 目标节点的ID
    :return: 包含路径上所有节点的列表
    """
    path = []
    current_node_id = node_id
    while current_node_id:  # 当current_node_id为None时停止循环，这意味着到达了根节点
        node = tree.get_node(current_node_id)  # 获取当前节点对象
        if node is None:
            raise ValueError("Node with ID '{}' not found in the tree.".format(current_node_id))
        path.append(node)  # 将当前节点添加到路径列表中
        current_node_id = tree.parent(current_node_id).identifier if tree.parent(current_node_id) else None

    return path[::-1]  # 返回反转的路径列表，以使其从根节点开始

# 示例使用
tree = Tree()
tree.create_node("Root", "root")  # 根节点
tree.create_node("Child 1", "child1", parent="root")
tree.create_node("Child 2", "child2", parent="child1")  # 添加更深层的子节点

path = get_path_to_node(tree, "child2")  # 获取从根节点到"child2"的路径
for node in path:
    print(node.tag)  # 打印路径上每个节点的标签















# # 测试____________________________________________________________________________________________________
# import json
# from json import dumps
# from treelib import Tree, Node
# from CenterSimulation.Utils.IBBEKeyRead import IBBEKeyRead, collect_node_values
# from NodeSimulation.Model.protocol.Securityprotocol import MessageDecoder
# from NodeSimulation.Model.protocol.Securityprotocol.protocol_utils.busid_to_secret import busid_to_secret, busid_to_IBBE_secret
# from pypbc import *
# from CenterSimulation.Utils.Json2Tree import json2tree
# from CenterSimulation.Model.PathReqAndEncryption import PathReqAndEncryption
# import logging
# from NodeSimulation.Model.ConnectProxy import ConnectProxy
#
# # 函数功能测试
# if __name__ == '__main__':
#     aaa = ConnectProxy("127.0.0.1", 20100)
#     delrequest = {
#         "affairs_id": "00001",
#         "user_id": "u00001",
#         "info_id": "a1b2c3d4e5",
#         "deleteMethod": "yingjianshanchu",
#         "deleteGranularity": "age",
#         "from_bus_id": "b1000"
#         # 为了弥补我们系统demo无法根据IP来进行节点区分，实际中是可行的
#     }
#     s = aaa.delNotifyReq(delrequest)
#     # 首先把接收到的数据loads一下，因为return的时候执行了jsonify
#     # loads之后变成了一个列表
#     s = json.loads(s)
#     print(type(s))
#
#
#
#
#     # 然后将删除通知树，IBBE密文，明文树loads一下，因为都进行了序列化
#     # s[0] = json.loads(s[0])  # 删除通知树
#     s[2] = json.loads(s[2])  # IBBE密文
#     # s[3] = json.loads(s[3])  # 明文树
#     print("删除通知树:")
#     print(s[0])
#     print(type(s[0]))
#     print("时间戳：")
#     print(s[1])
#     print(type(s[1]))
#     print("IBBE密文：")
#     print(s[2])
#     print(type(s[2]))
#     print("明文树:")
#     print(s[3])
#     print(type(s[3]))
#
#     # def add_node_from_dict(node_dict, tree, parent=None):
#     #     # 遍历字典中的每个节点
#     #     for node_id, content in node_dict.items():
#     #         # 创建当前节点
#     #         tree.create_node(tag=node_id, identifier=node_id, parent=parent)
#     #         # 如果存在子节点，递归添加子节点
#     #         if 'children' in content and content['children']:
#     #             for child in content['children']:
#     #                 add_node_from_dict(child, tree, parent=node_id)
#     #
#     #
#     # def build_tree(data_dict):
#     #     tree = Tree()
#     #     # 从提供的字典开始构建树
#     #     add_node_from_dict(data_dict, tree)
#     #     return tree
#     #
#     #
#     # # 重建树
#     # tree = build_tree(s[0])
#     # tree1 = build_tree(s[3])
#     # # 打印树以验证
#     # print(tree)
#     # print(tree1)
#
#     # tree = Tree()
#     #
#     # def add_nodes(parent_id, children):
#     #     for child in children:
#     #         if isinstance(child, dict):  # 如果子节点是字典，表示它有进一步的子节点
#     #             for child_id, grandchild in child.items():
#     #                 if "children" in grandchild:  # 如果有更深层的子节点
#     #                     tree.create_node(tag=child_id, identifier=child_id, parent=parent_id)
#     #                     add_nodes(child_id, grandchild["children"])
#     #                 else:  # 如果没有更深层的子节点，直接添加
#     #                     tree.create_node(tag=child_id, identifier=child_id, parent=parent_id)
#     #         else:  # 如果子节点不是字典，表示它是叶子节点
#     #             tree.create_node(tag=child, identifier=child, parent=parent_id)
#     #
#     #
#     # # 初始化根节点
#     # root_id = 'root'
#     # tree.create_node(tag=root_id, identifier=root_id)
#     #
#     # # 从根节点开始添加所有子节点
#     # add_nodes(root_id, s[0][root_id]['children'])
#     #
#     # print(tree)
#
#     tree = json2tree(s[0])
#     tree1 = json2tree(s[3])
#     print(tree)
#     print(type(tree))
#     print(tree1)
#     print(type(tree1))
#
#     S = collect_node_values(tree1)
#     logging.info("S列表如下:")
#     print(S)
#
#     # def aaa(from_bus_id, to_bus_id, time_stamp, plaintext, segment_tree):
#     #     print(from_bus_id + "--->" + to_bus_id)
#     #     next_bus_ip_list, next_segment_tree_list = decoder.treeDecode(from_bus_id, to_bus_id, time_stamp,plaintext, segment_tree)
#     #     for i, j in zip(next_bus_ip_list, next_segment_tree_list):
#     #         if i == "center":
#     #             break
#     #         else:
#     #             aaa(to_bus_id, i, time_stamp, plaintext, j)
#     #
#     # aaa('center', 'b1000',time_stamp, plaintext, segment_tree)
#
#     params, MSK, PK = IBBEKeyRead()
#     params = Parameters(params.__str__())
#
#     ID = 'b1000'
#     pairing1 = Pairing(params)
#     SK = Element(pairing1, G2, busid_to_IBBE_secret(ID))
#
#     ID = 'b1000'
#     payload = tuple(s[2])
#     print(payload)
#     print(type(payload))
#
#     Hdry = payload[0]
#     for i, (Hdr, y) in enumerate(Hdry):
#         Hdr[0] = Element(pairing1, G1, Hdr[0])
#         Hdr[1] = Element(pairing1, G2, Hdr[1])
#         Hdry[i] = (Hdr, y)
#
#     payload_list = list(payload)
#     payload_list[0] = Hdry
#     payload = tuple(payload_list)
#     pub_param = (S, SK, ID, PK)
#
#     decoder = MessageDecoder.Decoder()
#     decoder.setParams(params.__str__())
#     newPlaintext = ""
#     try:
#         newPlaintext = decoder.ibbeDecode(pub_param, payload)
#     except Exception as e:
#         print(e)
#
#     # newPlaintext是str形式，需要转换会dict格式
#     newPlaintext = json.loads(newPlaintext)
#     print(newPlaintext)
#     print(type(newPlaintext))
#
#     # plain = {'affairs_id': '00001', 'user_id': 'u00001', 'info_id': 'a1b2c3d4e5', 'deleteMethod': 'yingjianshanchu',
#     #          'deleteGranularity': 'age'}
#     plaintext = json.dumps(newPlaintext)
#
#
#     # plaintext = newPlaintext
#
#     def aaa(from_bus_id, to_bus_id, time_stamp, plaintext, segment_tree):
#         print(from_bus_id + "--->" + to_bus_id)
#         next_bus_ip_list, next_segment_tree_list = decoder.treeDecode(from_bus_id, to_bus_id, time_stamp, plaintext,
#                                                                       segment_tree)
#         print(next_bus_ip_list)
#         print(next_segment_tree_list[0])
#         print(next_segment_tree_list[1])
#         # for i, j in zip(next_bus_ip_list, next_segment_tree_list):
#         #     if i == "center":
#         #         break
#         #     else:
#         #         aaa(to_bus_id, i, time_stamp, plaintext, j)
#
#
#     time = s[1]
#     print(tree)
#     aaa('center', 'b1000', time, plaintext, tree)
