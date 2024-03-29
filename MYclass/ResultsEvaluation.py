import requests
import json
import time
import re

# 定义不同的getLogType值
log_types = [
    "getDelete_IntentLog",
    "getDelete_RequestLog",
    "getDelete_TriggerLog",
    "getDelete_NotificationLog",
    "getDelete_ConfirmationLog"
]

# 基本信息
# ip = "192.168.43.48"  # 源企业节点开放的ip
ip = "127.0.0.1"
port = 30000          # 源企业节点开放的port

url = f"http://{ip}:{port}/result/postx/endpointx"  # 替换为源企业节点的URL

# 遍历不同的getLogType
for log_type in log_types:
    loginfo = {
        "systemID": 1,
        "systemIP": "210.73.60.100",
        "time": "2020-08-01 08:00:00",
        "data": {
            "affairsID": "0001",
            "infoID": "0x0001",
            "getLogType": log_type
        },
        "dataHash": "56e3be093f377b9d984eef02a982d852d1bce062fdb505bcf87df46141fd80aa"
    }

    # 将字典转换为JSON格式的字符串
    # log = json.dumps(loginfo)

    # 发送POST请求
    response = requests.post(url, json=loginfo)

    # 检查响应
    if response.status_code == 200:
        print(f"POST请求成功，getLogType: {log_type}")
        print(response.text)
        content_disposition = response.headers.get('Content-Disposition')

        # 使用正则表达式从Content-Disposition中提取文件名
        print(content_disposition)
    else:
        print(f"POST请求失败，getLogType: {log_type}")
        print("响应状态码:", response.status_code)

    # time.sleep(5)


# import requests
# import json
# import argparse
#
# # 服务器URL
# SERVER_URL = 'http://192.168.12.6:3444'
#
# # 定义不同的日志类型
# LOG_TYPES = [
#     "Delete_Intent", "Delete_Request", "Delete_Trigger",
#     "Delete_Notification", "Delete_Confirmation", "Delete_Operation"
# ]
#
# def send_logs(infoID, log_type):
#     headers = {'Content-Type': 'application/json'}
#
#     payload = {
#         "systemID": 1,
#         "systemIP": "210.73.60.100",
#         "time": "2020-08-01 08:00:00",
#         "data": {
#         "infoID": infoID,
#         "getLogType": f"get{log_type}Log"
#         },
#         "dataHash": "56e3be093f377b9d984eef02a982d852d1bce062fdb505bcf87df46141fd80aa"
#     }
#
# # 发送请求
#     response = requests.post(SERVER_URL, data=json.dumps(payload), headers=headers)
#     response_data = response.json()
#
#  # 保存到本地文件
#     with open(f"{log_type}_log.json", 'w') as file:
#         json.dump(response_data, file, indent=4)
#
# if __name__ == '__main__':
#     parser = argparse.ArgumentParser(description="Send logs to a server")

# import logging
#
# # 配置日志输出格式
# logging.basicConfig(format='[%(asctime)s] - %(message)s', level=logging.INFO)
#
# # 打印信息
# logging.info('我是在进行测试')

# from datetime import datetime
#
# # 获取当前时间
# current_time = datetime.now()
#
# # 将时间格式化为字符串
# formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
#
# # 打印带有时间戳的信息
# print(f"[{formatted_time}] Your message here")
#
# from datetime import datetime
# import pprint
# # 获取当前时间
# current_time = datetime.now()
# dataTransferPath = [{"from": "b1000", "to": "b1001"},{"from": "b1000", "to": "b1003"},{"from": "b1001", "to": "b1002"},{"from": "b1003", "to": "b1004"}]
# # 将时间格式化为字符串，同时使用ANSI转义码设置颜色
# formatted_time = f"\033[91m{current_time.strftime('%Y-%m-%d %H:%M:%S')}\033[0m"
#
# # 打印带有红色时间戳的信息
# pprint.pprint(f"[{formatted_time}] - {dataTransferPath}")
# from pprint import PrettyPrinter
# import datetime
#
#
# # def pprint_with_timestamp(message, data):
# #     current_time = datetime.datetime.now()
# #     timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
# #
# #     # 打印空行
# #     print()
# #
# #     # 使用 PrettyPrinter 类设置缩进为 1
# #     pp = PrettyPrinter(indent=1)
# #
# #     # 打印带有时间戳的信息和数据结构
# #     print(f"[{timestamp}] {message}")
# #     pp.pprint(data)
# #
# #
# # # 示例用法
# # message = "这是带有时间戳的信息"
# # data = {"key1": "value1", "key2": [1, 2, 3], "key3": {"nested_key": "nested_value"}}
# # pprint_with_timestamp(message, data)
#
# # from collections import defaultdict
# # from treelib import Tree
# # from Json2Tree import json2tree
# #
# # def build_graph(dataTransferPath):
# #     graph = defaultdict(list)
# #     for edge in dataTransferPath:
# #         graph[edge['from']].append(edge['to'])
# #         graph[edge['to']].append(edge['from'])
# #     return graph
# #
# #
# # def dfs_tree(graph, current_node, visited, tree):
# #     visited.add(current_node)
# #     for neighbor in graph[current_node]:
# #         if neighbor not in visited:
# #             tree.create_node(identifier=neighbor, parent=current_node)
# #             dfs_tree(graph, neighbor, visited, tree)
# #
# #
# # def gen_tree_json(dataTransferPath, root):
# #     graph = build_graph(dataTransferPath)
# #
# #     tree = Tree()
# #     tree.create_node(identifier=root)  # 根节点
# #
# #     visited_nodes = set()
# #     dfs_tree(graph, root, visited_nodes, tree)
# #
# #     return tree.to_json()
#
#
# # # 示例使用
# # dataTransferPath = [
# #     {"from": "b1000", "to": "b1003"},
# #     {"from": "b1002", "to": "b1000"},
# #     {"from": "b1002", "to": "b1001"},
# #     {"from": "b1001", "to": "b1004"}
# # ]
# #
# # # 以 "b1004" 为根节点构建树
# # root_node = "b1003"
# # tree_json = gen_tree_json(dataTransferPath, root_node)
# # print(tree_json)
# # tree = json2tree(tree_json)
# # print(tree)
#
# import mysql.connector
#
# # 连接 MySQL 服务器
# connection = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     password="123456"
# )
#
# # 创建一个游标对象
# cursor = connection.cursor()ls
# # # processor = InfoMemory(host="localhost", user="root", port=3306, password="123456", database="project26")
# # # processor = InfoMemory(host="10.170.42.45", port=3306, user="myuser", password="mypassword", database="project26")
# # # processor.insert_record(delNotice["user_id"], delNotice["info_id"],delNotice["deleteMethod"],delNotice["deleteGranularity"],delNotice["deleteNotifyTree"],triggerType,Bus_id,Timememory,Countmemory)
# # 新建数据库的 SQL 语句
# database_name = "your_database_name"
# create_database_query = f"CREATE DATABASE {database_name}"
#
# # 执行 SQL 语句
# cursor.execute(create_database_query)
#
# # 关闭游标和连接
# cursor.close()
# connection.close()


# import subprocess
#
# # 要传递的参数
# file_name = "D:\\PycharmFiles\\pythonProject2\\MYclass\\Business.py"
# args_list = [
#     {"arg1": "b1000", "arg2": "20000"},
#     {"arg1": "b1001", "arg2": "20001"},
#     {"arg1": "b1002", "arg2": "20002"},
#     {"arg1": "b1003", "arg2": "20003"},
#     {"arg1": "b1004", "arg2": "20004"},
#     # 添加更多参数
# ]
# file_name1 = "D:\\PycharmFiles\\pythonProject2\\MYclass\\Central_authority.py"
# command = 'start cmd /k ""D:\\Python\\Interpret\\Scripts\\python.exe" "{}""'.format(file_name1)
# # 执行命令
# subprocess.Popen(command, shell=True)
#
# # 循环处理每个参数组合
# for args_dict in args_list:
#     # 获取参数值
#     arg1 = args_dict["arg1"]
#     arg2 = args_dict["arg2"]
#
#     # 构建启动命令
#     command = 'start cmd /k ""D:\\Python\\Interpret\\Scripts\\python.exe" "{}" {} {}"'.format(file_name, arg1, arg2)
#
#     # 执行命令
#     subprocess.Popen(command, shell=True)


# 删除日志请求getLog

# import requests
# import json
# import argparse
# import copy
# import re
#
# # 定义不同的服务器URL和对应的日志类型
# SERVER_LOG_MAPPING = {
#     'http://127.0.0.1:1111/getIntentLog': "Delete_Intent",
#     'http://127.0.0.1:2222/getRequestLog': "Delete_Request",
#     'http://127.0.0.1:3333/getTriggerLog': "Delete_Trigger",
#     'http://127.0.0.1:4444/getNotificationLog': "Delete_Notification",
#     'http://127.0.0.1:5555/getConfirmationLog': "Delete_Confirmation",
#     'http://127.0.0.1:6666/getOperationLog': "Delete_Operation",
#     # 添加其他服务器URL和对应的日志类型
# }
#
#
# def getLog(infoID):
#     headers = {'Content-Type': 'application/json'}
#
#     for server_url, log_type in SERVER_LOG_MAPPING.items():
#         payload = {
#             "systemID": 1,
#             "systemIP": "210.73.60.100",
#             "mainCMD": 1,
#             "subCMD": 32,
#             "evidenceID": "00032dab40af0c56d2fa332a4924d150",
#             "msgVersion": 4096,
#             "submittime": "2023-11-08 00:15:28",
#             "data": {
#                 "infoID": infoID,
#                 "getLogType": f"get{log_type}Log"
#             },
#             "dataHash": "56e3be093f377b9d984eef02a982d852d1bce062fdb505bcf87df46141fd80aa",
#             "datasign": "56e3be093f377b9d984eef02a982d852d1bce062fdb505bcf87df46141fd80aa"
#         }
#         print(payload)
#         # 复制payload对象
#         payload_copy = copy.deepcopy(payload)

        # # 发送请求
        # response = requests.post(server_url, data=json.dumps(payload), headers=headers)
        # 发送请求
        # response = requests.post(server_url, data=json.dumps(payload, ensure_ascii=False), headers=headers)
        #
        # if response.status_code == 200:
        #     try:
        #         response_data = response.json()  # 解析JSON字符串
        #
        #         for file_info in response_data:
        #             if isinstance(file_info, dict):  # 确保是字典类型
        #                 file_name = file_info.get("fileName")
        #                 if file_name:
        #                     with open(file_name, 'w') as file:
        #                         json.dump(file_info["content"], file, indent=4)
        #                 else:
        #                     print(f"No file name provided for response from {server_url}")
        #             else:
        #                 print(f"Unexpected data format from {server_url}")
        #     except json.JSONDecodeError:
        #         print(f"Error: Unable to parse JSON response from {server_url}")
        # else:
        #     print(f"Error: Request to {server_url} failed with status code {response.status_code}")

        # if response.status_code == 200:
        #     try:
        #         response_data = response.json()

        #         # 使用服务器提供的文件名保存文件
        #         for file_info in response_data:
        #             file_name = file_info.get("fileName")
        #             if file_name:
        #                 with open(file_name, 'w') as file:
        #                     json.dump(file_info, file, indent=4)
        #             else:
        #                 print(f"No file name provided for response from {server_url}")
        #     except json.JSONDecodeError:
        #         print(f"Error: Unable to parse JSON response from {server_url}")
        # else:
        #     print(f"Error: Request to {server_url} failed with status code {response.status_code}")
        # # 检查响应状态码
        # if response.status_code == 200:
        #     try:
        #         response_data = response.json()
        #         print(response_data)
        #         # 获取响应数据的文件名，使用客户端发送的JSON文件名
        #         file_name = re.sub(r"[^a-zA-Z0-9]", "_", f"{infoID}_XXX_{log_type}_log.json")

        #         # 保存响应数据到本地文件
        #         with open(file_name, 'w') as file:
        #             json.dump(response_data, file, indent=4)
        #         # 保存到本地文件
        #         #with open(f"{infoID}_{log_type}_log.json", 'w') as file:
        #             #json.dump(response_data, file, indent=4)
        #     except json.JSONDecodeError:
        #         print(f"Error: Unable to parse JSON response from {server_url}")
        # else:
        #     print(f"Error: Request to {server_url} failed with status code {response.status_code}")


# if __name__ == '__main__':
#     # parser = argparse.ArgumentParser(description="Send logs to multiple servers")
#     # parser.add_argument("infoID", help="Specify the infoID")
#     #
#     # args = parser.parse_args()
#
#     getLog("0x0002")

# from flask import Response
# from io import BytesIO
# import csv
#
# @app.route('/get-file')
# def get_file():
#     # 在内存中创建一个文件-like对象
#     proxy = BytesIO()
#
#     # 创建一个CSV写入器
#     writer = csv.writer(proxy)
#
#     # 写入一些CSV数据
#     writer.writerow(['Header1', 'Header2', 'Header3'])
#     writer.writerow(['Row1', 'Data1', 'Data2'])
#     writer.writerow(['Row2', 'Data3', 'Data4'])
#
#     # 移动到开始位置，以便发送文件的内容
#     proxy.seek(0)
#
#     # 创建一个生成器，从文件-like对象读取并生成响应
#     def generate():
#         yield from proxy
#         proxy.close()  # 关闭文件-like对象
#
#     # 发送响应
#     return Response(generate(), mimetype='text/csv', headers={"Content-Disposition": "attachment;filename=myfile.csv"})



