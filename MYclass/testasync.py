# import asyncio
import json

from flask import Flask,request

# async def fun1():
#     print("函数1")
#     await asyncio.sleep(5)
#     print("函数1结束")
#
# async def fun2():
#     print("函数2")
#
# task_list = [fun2(), fun1()]
# asyncio.run(asyncio.wait(task_list))

import datetime
import time

# 设置未来的时间点，例如在未来的10秒后继续执行
# future_time = datetime.datetime.now() + datetime.timedelta(seconds=9.5)
#
# print("程序开始执行")
#
# while datetime.datetime.now() < future_time:
#     # 检查当前时间是否已经达到了未来的时间点
#     time_remaining = (future_time - datetime.datetime.now()).total_seconds()
#     print(f"距离继续执行还有 {time_remaining:.2f} 秒")
#     time.sleep(1)  # 每秒检查一次
#
# print("程序继续执行")

# def find_node_and_children(tree, target_node_key):
#     if target_node_key in tree:
#         return tree[target_node_key]
#     for node_key, children in tree.items():
#         if isinstance(children, list):
#             for child in children:
#                 result = find_node_and_children(child, target_node_key)
#                 if result:
#                     return result
#
# # 示例数据
# deleteNotifytree = {
#     "b1000": [
#         {"b1001": [
#             {"b1002": []}
#         ]},
#         {"b1003": [
#             {"b1004": [{"b1005":[]}]}
#         ]}
#     ]
# }
#
# # 查找节点 "b1001" 及其子节点
# target_node_key = "b1004"
# result = find_node_and_children(deleteNotifytree, target_node_key)
#
# if result:
#     print(f"节点 {target_node_key} 及其子节点: {result}")
# else:
#     print(f"未找到节点 {target_node_key}")


# class Tree:
#     def __init__(self, tree_data):
#         self.tree_data = tree_data
#
#     def find_node_and_children(self, target_node_key):
#         return self._find_node_and_children(self.tree_data, target_node_key)
#
#     def _find_node_and_children(self, tree, target_node_key):
#         if target_node_key in tree:
#             return tree[target_node_key]
#         for node_key, children in tree.items():
#             if isinstance(children, list):
#                 for child in children:
#                     result = self._find_node_and_children(child, target_node_key)
#                     if result:
#                         return result
#         return None
#
# # 示例数据
# deleteNotifytree = {
#     "b1000": [
#         {"b1001": [
#             {"b1002": []}
#         ]},
#         {"b1003": [
#             {"b1004": []}
#         ]}
#     ]
# }
#
# # 创建 Tree 类的实例
# tree = Tree(deleteNotifytree)
#
# # 查找节点 "b1001" 及其子节点
# target_node_key = "b1003"
# result = tree.find_node_and_children(target_node_key)
#
# if result:
#     print(f"节点 {target_node_key} 及其子节点: {result}")
# else:
#     print(f"未找到节点 {target_node_key}")
#     print(result)
#
# userroute = Flask(__name__)
# @userroute.route("/")
# def hello():
#     print("hello")
#     # 创建一个画布
#     fig, ax = plt.subplots()
#
#     # 创建一个矩形
#     rectangle = patches.Rectangle((0.2, 0.3), 0.5, 0.4, linewidth=2, edgecolor='r', facecolor='none')
#
#     # 将矩形添加到画布上
#     ax.add_patch(rectangle)
#
#     # 设置坐标轴范围
#     ax.set_xlim(0, 1)
#     ax.set_ylim(0, 1)
#
#     # 添加标题和标签
#     plt.title("矩形图")
#     plt.xlabel("X轴")
#     plt.ylabel("Y轴")
#
#     # 显示图形
#     plt.show()
#
#
# if __name__ == '__main__':
#     userroute.run()
# class TreeNodeFinder:
#     def __init__(self, tree):
#         self.tree = tree
#
#     def find_parent(self, target_node_key, current_tree=None, parent_key=None):
#         if current_tree is None:
#             current_tree = self.tree
#
#         if target_node_key in current_tree:
#             return parent_key
#
#         for key, value in current_tree.items():
#             if isinstance(value, list):
#                 for subtree in value:
#                     result = self.find_parent(target_node_key, subtree, key)
#                     if result:
#                         return result
#
#         return None
#
# # 示例数据
# deleteNotifytree = {
#     "b1000": [
#         {"b1001": [
#             {"b1002": []}
#         ]},
#         {"b1003": [
#             {"b1004": [
#                 {"b1005":[]}
#             ]}
#         ]}
#     ]
# }
#
# # 创建 TreeNodeFinder 实例
# finder = TreeNodeFinder(deleteNotifytree)
#
# # 查找节点 "b1004" 的父节点
# target_node_key = "b1005"
# parent_node = finder.find_parent(target_node_key)
#
# if parent_node:
#     print(f"节点 {target_node_key} 的父节点是 {parent_node}")
# else:
#     print(f"未找到节点 {target_node_key} 的父节点")

# from cryptography.hazmat.backends import default_backend
# from cryptography.hazmat.primitives.asymmetric import rsa
# from cryptography.hazmat.primitives import serialization
# from cryptography.hazmat.primitives import hashes
# from cryptography.hazmat.primitives.asymmetric import padding
# import hashlib
#
# # 生成RSA密钥对（公钥和私钥）
# private_key = rsa.generate_private_key(
#     public_exponent=65537,
#     key_size=2048,
#     backend=default_backend()
# )
#
# # 获取私钥的序列化形式（可以保存到文件或发送给其他人）
# private_pem = private_key.private_bytes(
#     encoding=serialization.Encoding.PEM,
#     format=serialization.PrivateFormat.PKCS8,
#     encryption_algorithm=serialization.NoEncryption()
# )
#
# # 获取公钥
# public_key = private_key.public_key()
#
# # 要签名的字符串
# input_string = "Hello, World!"
#
# # 对字符串进行SHA-256哈希处理
# hash_object = hashlib.sha256()
# hash_object.update(input_string.encode("utf-8"))
# hash_result = hash_object.digest()
#
# # 使用私钥进行签名
# signature = private_key.sign(
#     hash_result,
#     padding.PSS(
#         mgf=padding.MGF1(hashes.SHA256()),
#         salt_length=padding.PSS.MAX_LENGTH
#     ),
#     hashes.SHA256()
# )
#
# # 打印签名
# print("签名:", signature.hex())
#
# # 使用公钥验证签名
# try:
#     public_key.verify(
#         signature,
#         hash_result,
#         padding.PSS(
#             mgf=padding.MGF1(hashes.SHA256()),
#             salt_length=padding.PSS.MAX_LENGTH
#         ),
#         hashes.SHA256()
#     )
#     print("签名验证成功，数据完整和未被篡改。")
# except:
#     print("签名验证失败，数据可能已被篡改。")

# recvAckDict = {
#     "affairs_id": [2, {
#                         "affairs_id": "1",
#                         "from_bus_id": "1",
#                         "to_bus_id": "2",
#                         "user_id": "231",
#                         "info_id": "445",
#                         "DataTransferPath path": "12321321",
#                         "DelConfirmSignatureDict":  {"bx1000":"0xasdas"}
#                       },
#                    {
#                        "affairs_id": "1",
#                        "from_bus_id": "5",
#                        "to_bus_id": "2",
#                        "user_id": "231",
#                        "info_id": "445",
#                        "DataTransferPath path": "12321321",
#                        "DelConfirmSignatureDict":  {"bx1001":"0xasdfas"}
#                    }]
# }
#
# DelConfirm = {
#     "affairs_id": recvAckDict["affairs_id"][1]["affairs_id"],  # 事务ID
#     "from_bus_id": "0001",  # 本节点ID
#     "to_bus_id": "0002",  # 父节点ID
#     "user_id": recvAckDict["affairs_id"][1]["user_id"],
#     "info_id": recvAckDict["affairs_id"][1]["info_id"],
#     "DataTransferPath path": recvAckDict["affairs_id"][1]["DataTransferPath path"],
#     "DelConfirmSignatureDict": {}  # string bus_id: string signature的集合
#     # 这里应该需要一个hash_result用来验证签名做对比
# }
# print(DelConfirm)

import csv

# 创建一个CSV文件并写入数据
# def create_database():
#     with open('ID.csv', 'w', newline='') as csvfile:
#         fieldnames = ['ID', 'Name', 'Age']
#         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#         writer.writeheader()
#         writer.writerow({'ID': 1, 'Name': 'Alice', 'Age': 25})
#         writer.writerow({'ID': 2, 'Name': 'Bob', 'Age': 30})
#         writer.writerow({'ID': 3, 'Name': 'Charlie', 'Age': 22})

# 查询数据库
# def query_database(name):
#     with open('ID.csv', 'r') as csvfile:
#         port = ""
#         reader = csv.DictReader(csvfile)
#         for row in reader:
#             if row['ID'] == "b1008":
#                 port = row['port']
#     print(port)
#
# # 主程序
# if __name__ == '__main__':
#     query_name = input("请输入要查询的ID：")
#     query_database(query_name)

# ip = "202.202.202.202"
# nextNode = ["b1002","b1003"]
# coroutines = []
# delNotice = {
#     "affairs_id": "123",
#     "user_id": "123",
#     "info_id": "123",
#     "from_bus_id": "123",
#     "to_bus_id": "",  # 此参数会在发送时被更新
#     "deleteMethod": "123",
#     "deleteGranularity": "123",
#     "deleteNotifyTree_path": "123" # 一个字典
# }
# for item in nextNode:
#     with open('ID.csv', 'r') as csvfile:
#         port = ""
#         reader = csv.DictReader(csvfile)
#         for row in reader:
#             if row['ID'] == item:  # 默认中心监管机构的ID是b1999
#                 port = row['port']
#     delNotice["to_bus_id"] = item
#     print(delNotice)
#     coroutines = coroutines+["delNotifyOther(ip, port, delNotice)"]
# print(coroutines)

# import csv
# from cryptography.hazmat.primitives import serialization
# from cryptography.hazmat.primitives.asymmetric import rsa
#
# # 生成一个RSA密钥对
# def generate_rsa_key_pair():
#     private_key = rsa.generate_private_key(
#         public_exponent=65537,
#         key_size=2048,
#     )
#     return private_key, private_key.public_key()
#
# # 将密钥对存储到CSV文件中
# def store_key_pair_to_csv(private_key, public_key, filename):
#     with open(filename, 'a', newline='') as csvfile:
#         fieldnames = ['Private Key', 'Public Key']
#         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#
#         private_pem = private_key.private_bytes(
#             encoding=serialization.Encoding.PEM,
#             format=serialization.PrivateFormat.TraditionalOpenSSL,
#             encryption_algorithm=serialization.NoEncryption()
#         )
#
#         public_pem = public_key.public_bytes(
#             encoding=serialization.Encoding.PEM,
#             format=serialization.PublicFormat.SubjectPublicKeyInfo
#         )
#
#         writer.writerow({'Private Key': private_pem.decode('utf-8'), 'Public Key': public_pem.decode('utf-8')})
#
# # 主程序
# if __name__ == '__main__':
#     num_key_pairs = 100
#     output_file = 'key_pairs.csv'
#
#     # 创建CSV文件并写入标题行
#     with open(output_file, 'w', newline='') as csvfile:
#         fieldnames = ['Private Key', 'Public Key']
#         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#         writer.writeheader()
#
#     # 生成并存储100对密钥
#     for _ in range(num_key_pairs):
#         private_key, public_key = generate_rsa_key_pair()
#         store_key_pair_to_csv(private_key, public_key, output_file)
#
#     print(f'生成并存储了{num_key_pairs}对RSA密钥对到{output_file}文件中。')
# 查询公钥
# import csv
# from cryptography.hazmat.primitives import hashes
# from cryptography.hazmat.primitives.asymmetric import padding
# from cryptography.hazmat.primitives import serialization
# import hashlib
# # 查询公私钥对
# def query_Publickey_pair_by_id(csv_filename, identifier):
#     with open(csv_filename, mode='r') as csv_file:
#         reader = csv.DictReader(csv_file)
#         for row in reader:
#             if row["ID"] == identifier:
#                 return row["Public Key"]
#     return None
#
# def query_Privatekey_pair_by_id(csv_filename, identifier):
#     with open(csv_filename, mode='r') as csv_file:
#         reader = csv.DictReader(csv_file)
#         for row in reader:
#             if row["ID"] == identifier:
#                 return row["Private Key"]
#     return None
# def sign_message(private_key_pem, message):
#     private_key = serialization.load_pem_private_key(
#         private_key_pem.encode(),
#         password=None
#     )
#     # message_hash = hashes.Hash(hashes.SHA256())
#     # message_hash.update(message.encode())
#     # hashed_message = message_hash.finalize()
#     # 将消息签名
#     signature = private_key.sign(
#         message,
#         padding.PSS(
#             mgf=padding.MGF1(hashes.SHA256()),
#             salt_length=padding.PSS.MAX_LENGTH
#         ),
#         hashes.SHA256()
#     )
#
#     return signature
#
#
# # 使用公钥进行签名验证
# def verify_signature(public_key_pem, hashed_message, signature):
#     public_key = serialization.load_pem_public_key(
#         public_key_pem.encode()
#     )
#
#     try:
#         public_key.verify(
#             signature,
#             hashed_message,
#             padding.PSS(
#                 mgf=padding.MGF1(hashes.SHA256()),
#                 salt_length=padding.PSS.MAX_LENGTH
#             ),
#             hashes.SHA256()
#         )
#         return True# 验证成功
#     except:
#         return False # 验证失败
#
# if __name__ == "__main__":
#     csv_filename = "key_pairs.csv"
#     identifier_to_query = "b1000"  # 指定要查询的标识ID
#
#     private_key = query_Privatekey_pair_by_id(csv_filename, identifier_to_query)
#     identifier_to_query = "b1001"
#     public_key = query_Publickey_pair_by_id(csv_filename, identifier_to_query)
#     if public_key and private_key:
#         print(f"公钥：\n{public_key}")
#         print(f"私钥：\n{private_key}")
#     else:
#         print(f"未找到标识ID为 {identifier_to_query} 的公私钥对。")
#
#
#
#     # 使用您的私钥进行签名
#     # private_key_pem = """-----BEGIN PRIVATE KEY-----
#     # # 在此处粘贴您的私钥PEM编码
#     # -----END PRIVATE KEY-----"""
#
#     message_to_sign = "要签名的消息"
#     message_hash = hashes.Hash(hashes.SHA256())
#     message_hash.update(message_to_sign.encode())
#     hashed_message = message_hash.finalize()
#     signature = sign_message(private_key, hashed_message)
#     print(signature)
#     # # 使用您的公钥进行签名验证
#     # public_key_pem = """-----BEGIN PUBLIC KEY-----
#     # # 在此处粘贴您的公钥PEM编码
#     # -----END PUBLIC KEY-----"""
#
#     if verify_signature(public_key, hashed_message, signature):
#         print("签名验证成功，消息未被篡改。")
#     else:
#         print("签名验证失败，消息可能已被篡改。")

from MYclass.DelTrigger import DelTrigger
from MYclass.Json2Tree import json2tree
from MYclass.Path2Json import gen_tree_json
import pymysql
# if __name__ =="__main__":
    # data = {
    #       "affairs_id": "0001",
    #       "user_id": "B00001",
    #       "deleteGranularity":"\u8f6f\u4ef6\u5220\u9664",
    #       "info_id": "0x0001",
    #       "source_bus_id": "b1002",
    #       "deleteMethod": "\u6309\u9700"
    #         }
    # trigger = DelTrigger()
    # if "time_limit" in data and "count_limit" not in data:
    #     deleteReq = trigger.timeTrigger(data)  # 函数返回值删除请求，为一个dict
    # elif "time_limit" not in data and "count_limit" in data:
    #     deleteReq = trigger.countTrigger(data)
    # else:
    #     deleteReq = trigger.deleteTrigger(data)
    # print(deleteReq)
    #
    #
    # def find_child_nodes(tree, target_node_id):
    #     child_nodes = []
    #
    #     def search_children(node):
    #         if isinstance(node, dict):
    #             for key, value in node.items():
    #                 if key == target_node_id:
    #                     if "children" in value:
    #                         child_nodes.extend(value["children"])
    #                 search_children(value)
    #         elif isinstance(node, list):
    #             for item in node:
    #                 search_children(item)
    #
    #     search_children(tree)
    #     return child_nodes
    #
    #
    # deleteNotifyTree = {
    #     "b1000": {
    #         "children": [
    #             {"b1001":
    #                  {"children":
    #                       ["b1002"]
    #                 }
    #             },
    #             {"b1003": {
    #                  "children":[
    #                      {"b1004":
    #                             {"children":
    #                                  ["b1005"]
    #                              }
    #                      }]
    #                 }
    #             }
    #         ]
    #     }
    # }
    #
    # # 查找节点"b1000"的子节点
    # target_node_id = "b1000"
    # child_nodes = find_child_nodes(deleteNotifyTree, target_node_id)
    # print(child_nodes)
    #
    # # 查找节点"b1001"的子节点
    # target_node_id = "b1004"
    # child_nodes = find_child_nodes(deleteNotifyTree, target_node_id)
    # print(child_nodes)
    # lis = [{'b1001': {'children': ['b1002']}}, {'b1003': {'children': [{'b1004': {'children': ['b1005']}}]}}]
    # keys_list = []
    # for dictionary in lis:
    #     for key in dictionary.keys():
    #         keys_list.append(key)
    #
    # print(keys_list)
    #
    # # 删除通知生成与分发
    # # (1) 首先生成删除通知
    # # (2) 当前节点，通过deleteNotifyTree,得到后继节点，即后面应该发给那些节点（如果当前节点直接就是叶子节点，则不需要转发，直接返回一个true）
    # dataTransferPath = [
    #     {"from": "b1000", "to": "b1001"},
    #     {"from": "b1000", "to": "b1003"},
    #     {"from": "b1001", "to": "b1002"},
    #     {"from": "b1003", "to": "b1004"}
    # ]
    # Bus_id = "b1000"
    # deleteNotifyTree = gen_tree_json(dataTransferPath, Bus_id)
    # print(deleteNotifyTree)
    # tree = json2tree(deleteNotifyTree)
    # print(tree)
    # nextNode = [i._identifier for i in tree.children("b1000")]
    # print(nextNode)
    # node = tree.parent("b1003")
    # print(node)
    # node = node._identifier
    # print(node)
    # recvAckDict = {'0001': [2, {'b1001': '985fd9cfb94e0', 'b1002': '8d9fddd'}, {'b1003': '24d28ca763', 'b1004': '4341164bbb51c0'}]}
    # receive = len(recvAckDict['0001'])
    # print(receive)

    # db = pymysql.connect(host='localhost', user='root', password='123456', db='project26', port=3306)
    # cursor = db.cursor()
    # cursor.execute('SELECT VERSION()')
    # data = cursor.fetchone()
    # print("版本号", data)
    # db.close
    # 创建一个空的参数列表
    # parameter_list = []
    #
    # # 生成100个参数对
    # for i in range(1, 100):
    #     param1 = f"b10{i:02d}"
    #     param2 = f"200{i:02d}"
    #     parameter_list.append([param1, param2])
    #
    # # 打印生成的参数列表（可选）
    # for params in parameter_list:
    #     print(params)

import socket
app1 = Flask(__name__)
import pprint
@app1.route('/test3', methods=['POST'])
def page2():
    print("测试成功")
    loginfo = request.json
    loginfo = json.loads(loginfo)
    pprint.pprint(loginfo)
    return '删除效果测评系统收到数据！'


if __name__ == '__main__':
    app1.run(host='127.0.0.1', port=50000)

# socket.gethostbyname(socket.gethostname())
# print(socket.gethostbyname(socket.gethostname()))
