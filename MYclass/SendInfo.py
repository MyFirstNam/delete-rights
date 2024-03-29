import configparser
from pprint import pprint

from flask import request, Blueprint, Flask, jsonify
import requests
import json
from InfoMemory import InfoMemory
from Json2Tree import json2tree
import threading
import socket
from datetime import datetime
from flask import Response
from io import BytesIO
import json

sendInfo = Flask(__name__)
# todo 每次启动路由，标识当前路由（企业）ID，通过外部标识输入参数
Bus_id = "b1000"

# recvAckDictLock = threading.Lock()        暂时先不考虑竞争关系，删除效果评测系统不会同时发俩个请求
# 专门用于接收来自删除效果评测系统的路由
# @sendInfo.route("/result/postx/endpointx", methods=['POST'])
# def Logsend():
#     loginfo = request.json
#     # loginfo = json.loads(loginfo)
#     print(f"日志请求信息为：{loginfo}")
#     if loginfo is None:
#         return jsonify({"error": "Invalid JSON data"}), 400
#
#     # ip = "127.0.0.1"  # 删除效果评测系统开放的ip
#     # port = 50000
#     # 计划不采用post的方式发送查询结果，直接return的方式返回
#
#     # 创建ConfigParser对象
#     config = configparser.ConfigParser()
#     # 读取配置文件
#     config.read('config.ini')
#     # 从配置文件中获取值
#     host = config.get('Database', 'host')
#     user = config.get('Database', 'user')
#     password = config.get('Database', 'password')
#     mysqlport = config.getint('Database', 'port')
#     database = config.get('Database', 'database_prefix')
#     database = database + Bus_id
#
#     # 这里没有进行数据库是否存在，当时的设计是，只有存证的时候需要判断是否数据库存在，在提供日志的时候没有考虑这个
#     # 之后也可以加入，在提供日志的时候，也判断一下是否数据库存在
#
#     loginfo = loginfo["data"]
#     # loginfo["userID"] = "b00002"  当时为了和删除效果评测系统模拟测试，给定的一个数值
#     if loginfo["getLogType"] == "getDelete_IntentLog":
#         processor = InfoMemory(host=host, user=user, port=mysqlport, password=password, database=database)
#         try:
#             data = processor.search_IntentLog(loginfo["affairsID"], loginfo["infoID"])
#             intent_log = {
#                     "affairsID": loginfo["affairsID"],
#                     "userID": data[0][0],
#                     "infoID": loginfo["infoID"],
#                     "deleteMethod": data[0][1],
#                     "deleteIntention": data[0][0]+"请求删除其"+loginfo["infoID"]+"信息",
#                     "deleteGranularity": data[0][2],
#                     "sourceDomainID": data[0][3],
#                     "timeLimit": data[0][4],
#                     "countLimit": data[0][5]
#             }
#             intent_log = {
#                     "systemID": 0x40000000,
#                     "systemIP": socket.gethostbyname(socket.gethostname()),
#                     "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#                     "data": intent_log,
#                     "dataHash": "56e3be093f377b9d984eef02a982d852d1bce062fdb505bcf87df46141fd80aa"
#             }
#             # intent_log = json.dumps(intent_log)
#             # url = f"http://{ip}:{port}/test3"  # 替换为删除效果评测系统的实际目标URL
#             # response = requests.post(url, json=intent_log)
#             # if response.status_code == 200:
#             #     print("POST请求成功")
#             #     print(response.text)
#             # else:
#             #     print("POST请求失败")
#             #     print("响应状态码:", response.status_code)
#             proxy = BytesIO()
#             json_str = json.dumps(intent_log)
#             json_bytes = json_str.encode('utf-8')  # 编码为UTF-8
#
#             # 将字节写入文件-like对象
#             proxy.write(json_bytes)
#
#             # 将JSON数据写入文件-like对象
#             # 移动到开始位置，以便发送文件的内容
#             proxy.seek(0)
#
#             # 创建一个生成器，从文件-like对象读取并生成响应
#
#             def generate():
#                 yield from proxy
#                 proxy.close()  # 关闭文件-like对象
#
#             filename = loginfo["infoID"]+"_"+loginfo["affairsID"]+"_Delete_Intent_log.json"
#             # 发送响应
#             return Response(generate(), mimetype='application/json',
#                             headers={
#                                 "Content-Disposition": f"attachment;filename={filename}"})
#             # 这里json文件的名字需要改
#         except Exception as e:
#             return (f"数据查询不存在")
#
#     elif loginfo["getLogType"] == "getDelete_RequestLog":
#         processor = InfoMemory(host=host, user=user, port=mysqlport, password=password, database=database)
#         try:
#             data = processor.search_ReqestLog(loginfo["affairsID"], loginfo["infoID"])
#             request_log = {
#                 "affairsID": loginfo["affairsID"],
#                 "userID": data[0][0],
#                 "infoID": loginfo["infoID"],
#                 "deleteMethod": data[0][1],
#                 "deleteGranularity": data[0][2],
#                 "sourceDomainID": data[0][3],
#                 "timeLimit": data[0][4],
#                 "countLimit": data[0][5]
#             }
#             request_log = {
#                     "systemID": 0x40000000,
#                     "systemIP": socket.gethostbyname(socket.gethostname()),
#                     "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#                     "data": request_log,
#                     "dataHash": "56e3be093f377b9d984eef02a982d852d1bce062fdb505bcf87df46141fd80aa"
#             }
#             # request_log = json.dumps(request_log)
#             # url = f"http://{ip}:{port}/test3"  # 替换为删除效果评测系统的实际目标URL
#             # response = requests.post(url, json=request_log)
#             # if response.status_code == 200:
#             #     print("POST请求成功")
#             #     print(response.text)
#             # else:
#             #     print("POST请求失败")
#             #     print("响应状态码:", response.status_code)
#             proxy = BytesIO()
#             json_str = json.dumps(request_log)
#             json_bytes = json_str.encode('utf-8')  # 编码为UTF-8
#
#             # 将字节写入文件-like对象
#             proxy.write(json_bytes)
#
#             # 将JSON数据写入文件-like对象
#             # 移动到开始位置，以便发送文件的内容
#             proxy.seek(0)
#
#             # 创建一个生成器，从文件-like对象读取并生成响应
#
#             def generate():
#                 yield from proxy
#                 proxy.close()  # 关闭文件-like对象
#
#             filename = loginfo["infoID"]+"_"+loginfo["affairsID"]+"_Delete_Request_log.json"
#             # 发送响应
#             return Response(generate(), mimetype='application/json',
#                             headers={
#                                 "Content-Disposition": f"attachment;filename={filename}"})
#
#         except Exception as e:
#             return(f"数据查询不存在")
#
#     elif loginfo["getLogType"] == "getDelete_TriggerLog":
#         processor = InfoMemory(host=host, user=user, port=mysqlport, password=password, database=database)
#         try:   # 已经改到这里
#             data = processor.search_TriggerLog(loginfo["affairsID"], loginfo["infoID"])
#             trigger_log = {
#                 "affairsID": loginfo["affairsID"],
#                 "userID": data[0][0],
#                 "infoID": loginfo["infoID"],
#                 "deleteMethod": data[0][1],
#                 "deleteGranularity": data[0][2],
#                 "deleteTriggers": data[0][3],
#             }
#             trigger_log = {
#                     "systemID": 0x40000000,
#                     "systemIP": socket.gethostbyname(socket.gethostname()),
#                     "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#                     "data": trigger_log,
#                     "dataHash": "56e3be093f377b9d984eef02a982d852d1bce062fdb505bcf87df46141fd80aa"
#             }
#             # trigger_log = json.dumps(trigger_log)
#             # url = f"http://{ip}:{port}/test3"  # 替换为删除效果评测系统的实际目标URL
#             # response = requests.post(url, json=trigger_log)
#             # if response.status_code == 200:
#             #     print("POST请求成功")
#             #     print(response.text)
#             # else:
#             #     print("POST请求失败")
#             #     print("响应状态码:", response.status_code)
#             proxy = BytesIO()
#             json_str = json.dumps(trigger_log)
#             json_bytes = json_str.encode('utf-8')  # 编码为UTF-8
#
#             # 将字节写入文件-like对象
#             proxy.write(json_bytes)
#
#             # 将JSON数据写入文件-like对象
#             # 移动到开始位置，以便发送文件的内容
#             proxy.seek(0)
#             # 创建一个生成器，从文件-like对象读取并生成响应
#
#             def generate():
#                 yield from proxy
#                 proxy.close()  # 关闭文件-like对象
#
#             filename = loginfo["infoID"]+"_"+loginfo["affairsID"]+"_Delete_Trigger_log.json"
#             # 发送响应
#             return Response(generate(), mimetype='application/json',
#                             headers={"Content-Disposition": f"attachment;filename={filename}"})
#
#         except Exception as e:
#             return(f"数据查询不存在")
#
#     elif loginfo["getLogType"] == "getDelete_NotificationLog":
#         processor = InfoMemory(host=host, user=user, port=mysqlport, password=password, database=database)
#         try:
#             data = processor.search_notifyLog(loginfo["affairsID"], loginfo["infoID"])
#             notification_log = {
#                 "affairsID": loginfo["affairsID"],
#                 "userID": data[0][0],
#                 "infoID": loginfo["infoID"],
#                 "deleteMethod": data[0][1],
#                 "deleteGranularity": data[0][2],
#                 "deleteNotifyTree": data[0][3],
#             }
#             notification_log = {
#                     "systemID": 0x40000000,
#                     "systemIP": socket.gethostbyname(socket.gethostname()),
#                     "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#                     "data": notification_log,
#                     "dataHash": "56e3be093f377b9d984eef02a982d852d1bce062fdb505bcf87df46141fd80aa"
#             }
#
#             # notification_log = json.dumps(notification_log)
#             # url = f"http://{ip}:{port}/test3"  # 替换为删除效果评测系统的实际目标URL
#             # response = requests.post(url, json=notification_log)
#             # if response.status_code == 200:
#             #     print("POST请求成功")
#             #     print(response.text)
#             # else:
#             #     print("POST请求失败")
#             #     print("响应状态码:", response.status_code)
#             proxy = BytesIO()
#             json_str = json.dumps(notification_log)
#             json_bytes = json_str.encode('utf-8')  # 编码为UTF-8
#
#             # 将字节写入文件-like对象
#             proxy.write(json_bytes)
#
#             # 将JSON数据写入文件-like对象
#             # 移动到开始位置，以便发送文件的内容
#             proxy.seek(0)
#             # 创建一个生成器，从文件-like对象读取并生成响应
#
#             def generate():
#                 yield from proxy
#                 proxy.close()  # 关闭文件-like对象
#
#             filename = loginfo["infoID"]+"_"+loginfo["affairsID"]+"_Delete_Notification_log.json"
#             # 发送响应
#             return Response(generate(), mimetype='application/json',
#                             headers={"Content-Disposition": f"attachment;filename={filename}"})
#
#         except Exception as e:
#             return(f"数据查询不存在")
#
#     elif loginfo["getLogType"] == "getDelete_ConfirmationLog":
#         # 第一个版本
#         # processor = InfoMemory(host="localhost", user="root", port=3306, password="123456", database="project26")
#         # data = processor.search_confirmLog(loginfo["userID"], loginfo["infoID"])
#         # confirm_log = {
#         #     "userID": loginfo["userID"],
#         #     "infoID": loginfo["infoID"],
#         #     "deleteMethod": data[0][0],
#         #     "deleteGranularity": data[0][1],
#         #     "deleteTransferTree": data[0][2],
#         #     "delConfSigDict": data[0][3]
#         # }
#         # confirm_log = {
#         #         "systemID": 0x40000000,
#         #         "systemIP": socket.gethostbyname(socket.gethostname()),
#         #         "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#         #         "data": confirm_log,
#         #         "dataHash": "56e3be093f377b9d984eef02a982d852d1bce062fdb505bcf87df46141fd80aa"
#         # }
#         # confirm_log = json.dumps(confirm_log)
#         # url = f"http://{ip}:{port}/test3"  # 替换为删除效果评测系统的实际目标URL
#         # response = requests.post(url, json=confirm_log)
#         # if response.status_code == 200:
#         #     print("POST请求成功")
#         #     print(response.text)
#         # else:
#         #     print("POST请求失败")
#         #     print("响应状态码:", response.status_code)
#         # 第二个版本
#         processor = InfoMemory(host=host, user=user, port=mysqlport, password=password, database=database)
#         # data = processor.searchinfoall(loginfo["userID"], loginfo["infoID"])
#         try:
#             # data = processor.searchinfoall(loginfo["userID"], loginfo["infoID"])
#             data = processor.search_confirmLog(loginfo["affairsID"], loginfo["infoID"])
#             title = "企业节点对信息" + loginfo["infoID"] + "进行删除通知"
#             abstract = f"企业节点" + data[0][8]+ "通过" + data[0][7] + "接受" + "用户" + data[0][1] + "删除" + data[0][2] + "信息的请求,进行删除通知,通知完成"
#             # deleteIntention = data[0][0] + "请求删除其身份证信息"
#             memorydata = {
#                 "systemID": 0x40000000,
#                 "systemIP": socket.gethostbyname(socket.gethostname()),
#                 "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#                 "data": {
#                     # "globalID": "时间戳+随机数+产生信息系统名字",
#                     "affairsID": loginfo["affairsID"],
#                     "title": title,
#                     "abstract": abstract,
#                     "keyWords": "删除通知",
#                     "category": "4-1-1",
#                     "userID": data[0][1],
#                     "infoID": loginfo["infoID"],
#                     "deleteGranularity": data[0][4],
#                     # "deleteIntention": deleteIntention,
#                     # "deleteTriggers": data[0][6],
#                     "deleteConfirmation": "200",
#                     "deleteMethod": data[0][3],
#                     "deleteNotifyTree": data[0][5],
#                     "delConfirmSignatureDict": data[0][6]
#                 },
#                 "dataHash": "56e3be093f377b9d984eef02a982d852d1bce062fdb505bcf87df46141fd80aa",
#
#             }
#
#             pprint(memorydata)
#             # confirm_log = json.dumps(memorydata)
#             # return confirm_log
#             # url = f"http://{ip}:{port}/test3"  # 替换为删除效果评测系统的实际目标URL
#             # response = requests.post(url, json=confirm_log)
#             # if response.status_code == 200:
#             #     print("POST请求成功")
#             #     print(response.text)
#             # else:
#             #     print("POST请求失败")
#             #     print("响应状态码:", response.status_code)
#             # return confirm_log
#
#
#             # 准备一些JSON数据
#             # data = {
#             #     "key1": "value1",
#             #     "key2": "value2"
#             # }
#
#             # 在内存中创建一个文件-like对象
#             proxy = BytesIO()
#             json_str = json.dumps(memorydata)
#             json_bytes = json_str.encode('utf-8')  # 编码为UTF-8
#
#             # 将字节写入文件-like对象
#             proxy.write(json_bytes)
#
#             # 将JSON数据写入文件-like对象
#             # 移动到开始位置，以便发送文件的内容
#             proxy.seek(0)
#             # 创建一个生成器，从文件-like对象读取并生成响应
#
#             def generate():
#                 yield from proxy
#                 proxy.close()  # 关闭文件-like对象
#
#             filename = loginfo["infoID"]+"_"+loginfo["affairsID"]+"_Delete_Confirmation_log.json"
#             # 发送响应
#             return Response(generate(), mimetype='application/json',
#                             headers={"Content-Disposition": f"attachment;filename={filename}"})
#
#         except Exception as e:
#             print(e)
#             return(f"数据查询不存在")
#
#     else:
#         print("请求数据错误！")
#
#     return "删除效果评测系统推送测试成功！"
#
#
# # 路由：/getOperationLog
# # 功能：根据请求数据获取操作日志
# # 输入：
# #    无（使用 Flask 的 request.get_json() 获取输入数据）
# # 输出：
# #    JSON - 返回操作日志或错误信息
# @sendInfo.route('/getOperationLog', methods=['POST'])
# def get_operation_log():
#     try:
#         # 从 POST 请求中解析 JSON 数据
#         data = request.get_json()
#
#         # 打印请求信息
#         print(data)
#
#         # 解析基本字段
#         # 假设 data 是一个字典，包含各种可能的键值对
#
#         # 检查是否存在 'systemID'，如果存在，则获取 system_id 的值
#         if 'systemID' in data:
#             system_id = data.get('systemID')  # 系统ID
#
#         # 检查是否存在 'systemIP'，如果存在，则获取 system_ip 的值
#         if 'systemIP' in data:
#             system_ip = data.get('systemIP')  # 系统IP地址
#
#         # 检查是否存在 'mainCMD'，如果存在，则获取 main_cmd 的值
#         if 'mainCMD' in data:
#             main_cmd = data.get('mainCMD')  # 主命令
#
#         # 检查是否存在 'subCMD'，如果存在，则获取 sub_cmd 的值
#         if 'subCMD' in data:
#             sub_cmd = data.get('subCMD')  # 子命令
#
#         # 检查是否存在 'evidenceID'，如果存在，则获取 evidence_id 的值
#         if 'evidenceID' in data:
#             evidence_id = data.get('evidenceID')  # 证据ID
#
#         # 检查是否存在 'msgVersion'，如果存在，则获取 msg_version 的值
#         if 'msgVersion' in data:
#             msg_version = data.get('msgVersion')  # 消息版本
#
#         # 检查是否存在 'submittime'，如果存在，则获取 submittime 的值
#         if 'submittime' in data:
#             submittime = data.get('submittime')  # 提交时间
#
#         # 检查是否存在 'dataHash'，如果存在，则获取 data_hash 的值
#         if 'dataHash' in data:
#             data_hash = data.get('dataHash')  # 数据哈希
#
#         # 检查是否存在 'datasign'，如果存在，则获取 datasign 的值
#         if 'datasign' in data:
#             datasign = data.get('datasign')  # 数据签名
#
#         # 对infoID的解析
#         # 检查 'data' 键是否存在于 data 字典中且其值是否为一个字典
#         if 'data' in data and isinstance(data['data'], dict):
#             # 提取 'affairsID' 字段
#             # 如果 'data' 字典中存在 'affairsID'，则获取其值，否则设为默认空字符串
#             affairsID = data['data'].get('affairsID', '')
#
#             # 提取 'infoID' 字段
#             # 如果 'data' 字典中存在 'infoID'，则获取其值，否则设为默认空字符串
#             infoID = data['data'].get('infoID', '')
#
#             # 提取 'time' 字段
#             # 如果 'data' 字典中存在 'time'，则获取其值，否则设为默认空字符串
#             time_str = data['data'].get('time', '')
#         else:
#             # 如果 'data' 键不存在或其值不是字典，则将所有字段设为默认空字符串
#             affairsID = ''
#             infoID = ''
#             time_str = ''
#
#         # 特别处理 'data' 字典内的 'time' 字段
#         start_time, end_time = None, None
#         if 'to' in time_str:
#             start_time_str, end_time_str = time_str.split(' to ')
#             start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
#             end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S')
#
#         # 使用datetime.strptime()方法将start_time_str和end_time_str转换为datetime对象，
#         # 使用指定的日期时间格式 '%Y-%m-%d %H:%M:%S'
#
#         # 打印起止点时间
#             print("起止点时间为:"+ start_time +"到："+ end_time)
#
#         #  这行是操作数据库
#         # db_model = OperationLogModel("127.0.0.1", "root", "123456", "assured_deletion")
#         #
#         # # 第一种情况，根据infoID和affairsID查询指定的一条信息
#         # if infoID and affairsID:
#         #     result_json = db_model.get_records_by_infoID_affairsID(infoID, affairsID)
#         #
#         # elif not infoID:
#         #     result_json = db_model.get_records_by_time_period(start_time, end_time)
#         #
#         # elif not time_str:
#         #     result_json = db_model.get_records_by_infoID(infoID)
#         #
#         # else:
#         #     return jsonify({"error": "wrong request format"}), 500
#         #
#         # op_log = db_model.format_log(result_json)
#         #
#         # return jsonify(op_log)
#
#
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


# todo  从这里开始,往上的代码都是老版本的代码，作用不大

# 路由：/getIntentLog
# 功能：根据请求数据获取删除意图日志
# 输入：
#    无（使用 Flask 的 request.get_json() 获取输入数据）
# 输出：
#    JSON - 返回删除意图日志或错误信息
@sendInfo.route('/getIntentLog', methods=['POST'])
def get_intention_log():
    try:
        # 从 POST 请求中解析 JSON 数据
        data = request.get_json()
        # 打印接收到的请求信息
        print(data)

        # 解析基本字段
        # 假设 data 是一个字典，包含各种可能的键值对

        # # 检查是否存在 'systemID'，如果存在，则获取 system_id 的值
        # if 'systemID' in data:
        #     system_id = data.get('systemID')  # 系统ID
        #
        # # 检查是否存在 'systemIP'，如果存在，则获取 system_ip 的值
        # if 'systemIP' in data:
        #     system_ip = data.get('systemIP')  # 系统IP地址
        #
        # # 检查是否存在 'mainCMD'，如果存在，则获取 main_cmd 的值
        # if 'mainCMD' in data:
        #     main_cmd = data.get('mainCMD')  # 主命令
        #
        # # 检查是否存在 'subCMD'，如果存在，则获取 sub_cmd 的值
        # if 'subCMD' in data:
        #     sub_cmd = data.get('subCMD')  # 子命令
        #
        # # 检查是否存在 'evidenceID'，如果存在，则获取 evidence_id 的值
        # if 'evidenceID' in data:
        #     evidence_id = data.get('evidenceID')  # 证据ID
        #
        # # 检查是否存在 'msgVersion'，如果存在，则获取 msg_version 的值
        # if 'msgVersion' in data:
        #     msg_version = data.get('msgVersion')  # 消息版本
        #
        # # 检查是否存在 'submittime'，如果存在，则获取 submittime 的值
        # if 'submittime' in data:
        #     submittime = data.get('submittime')  # 提交时间
        #
        # # 检查是否存在 'dataHash'，如果存在，则获取 data_hash 的值
        # if 'dataHash' in data:
        #     data_hash = data.get('dataHash')  # 数据哈希
        #
        # # 检查是否存在 'datasign'，如果存在，则获取 datasign 的值
        # if 'datasign' in data:
        #     datasign = data.get('datasign')  # 数据签名



        # 对infoID的解析
        # 检查 'data' 键是否存在于 data 字典中且其值是否为一个字典
        if 'data' in data and isinstance(data['data'], dict):
            # 提取 'affairsID' 字段
            # 如果 'data' 字典中存在 'affairsID'，则获取其值，否则设为默认空字符串
            affairsID = data['data'].get('affairsID', '')

            # 提取 'infoID' 字段
            # 如果 'data' 字典中存在 'infoID'，则获取其值，否则设为默认空字符串
            infoID = data['data'].get('infoID', '')

            # 提取 'time' 字段
            # 如果 'data' 字典中存在 'time'，则获取其值，否则设为默认空字符串
            time_str = data['data'].get('time', '')
        else:
            # 如果 'data' 键不存在或其值不是字典，则将所有字段设为默认空字符串
            affairsID = ''
            infoID = ''
            time_str = ''

        # 特别处理 'data' 字典内的 'time' 字段
        start_time, end_time = None, None
        if 'to' in time_str:
            start_time_str, end_time_str = time_str.split(' to ')
            start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
            end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S')

        print(start_time, end_time)

        #  这行是操作数据库  todo 之后具体怎么操作库还得改
        #  db_model = OperationLogModel("127.0.0.1", "root", "123456", "assured_deletion")

        intent_log = {
            "affairsID": "16881233",
            "userID": "b00001",
            "infoID": "0c1d2e3f4g5h",
            "deleteMethod": "软件删除",
            "deleteIntention": "b00001" + "请求删除其" + "0c1d2e3f4g5h" + "信息",
            "deleteGranularity": "age",
            "sourceDomainID": "b1000",
            "timeLimit": "0000000",
            "countLimit": 0
        }
        intent_log = {
            "systemID": 0x40000000,
            "systemIP": socket.gethostbyname(socket.gethostname()),
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data": intent_log,
            "dataHash": "56e3be093f377b9d984eef02a982d852d1bce062fdb505bcf87df46141fd80aa"
        }


        if infoID and affairsID:
            # 指定的infoID和affairsID，2个日志，非源域的，得判断是不是源域
            # result_json = db_model.get_records_by_infoID_affairsID(infoID, affairsID)
            # todo 其实对于删除意图日志，这条永远不会被执行
            result_json = [intent_log]
        elif not infoID:
            # 只有时间段，也是默认源域，5种，所以查询的时候，得判断是不是源域
            # result_json = db_model.get_records_by_time_period(start_time, end_time)
            result_json = [intent_log]
        elif not time_str:
            # 纯infoID，默认此时请求，所有源域的信息，可能有不同的affairsID，5种，所以查询的时候，得判断是不是源域
            # result_json = db_model.get_records_by_infoID(infoID)
            result_json = [intent_log]
        else:
            return jsonify({"error": "wrong request format"}), 500

        # 数据格式精简
        # op_log = db_model.format_log(result_json)

        # 给删除效果评测系统返回的只能是列表
        return jsonify(result_json)

        # filename=infoID+"_"+affairsID

        # # 构建文件路径
        # file_path = os.path.join('log', f"{filename}.json")

        # # 检查文件是否存在
        # if os.path.exists(file_path):
        #     with open(file_path, 'r') as file:
        #         log_data = json.load(file)
        #         return jsonify(log_data)
        # else:
        #     return jsonify({"error": "Log not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500




# 路由：/getRequestLog
# 功能：根据请求数据获取删除请求日志
# 输入：
#    无（使用 Flask 的 request.get_json() 获取输入数据）
# 输出：
#    JSON - 返回删除请求日志或错误信息
@sendInfo.route('/getRequestLog', methods=['POST'])
def get_request_log():
    try:
        # 从 POST 请求中解析 JSON 数据
        data = request.get_json()
        # 打印接收到的请求信息
        print(data)

        # 解析基本字段
        # 假设 data 是一个字典，包含各种可能的键值对

        # # 检查是否存在 'systemID'，如果存在，则获取 system_id 的值
        # if 'systemID' in data:
        #     system_id = data.get('systemID')  # 系统ID
        #
        # # 检查是否存在 'systemIP'，如果存在，则获取 system_ip 的值
        # if 'systemIP' in data:
        #     system_ip = data.get('systemIP')  # 系统IP地址
        #
        # # 检查是否存在 'mainCMD'，如果存在，则获取 main_cmd 的值
        # if 'mainCMD' in data:
        #     main_cmd = data.get('mainCMD')  # 主命令
        #
        # # 检查是否存在 'subCMD'，如果存在，则获取 sub_cmd 的值
        # if 'subCMD' in data:
        #     sub_cmd = data.get('subCMD')  # 子命令
        #
        # # 检查是否存在 'evidenceID'，如果存在，则获取 evidence_id 的值
        # if 'evidenceID' in data:
        #     evidence_id = data.get('evidenceID')  # 证据ID
        #
        # # 检查是否存在 'msgVersion'，如果存在，则获取 msg_version 的值
        # if 'msgVersion' in data:
        #     msg_version = data.get('msgVersion')  # 消息版本
        #
        # # 检查是否存在 'submittime'，如果存在，则获取 submittime 的值
        # if 'submittime' in data:
        #     submittime = data.get('submittime')  # 提交时间
        #
        # # 检查是否存在 'dataHash'，如果存在，则获取 data_hash 的值
        # if 'dataHash' in data:
        #     data_hash = data.get('dataHash')  # 数据哈希
        #
        # # 检查是否存在 'datasign'，如果存在，则获取 datasign 的值
        # if 'datasign' in data:
        #     datasign = data.get('datasign')  # 数据签名

        # 对infoID的解析
        # 检查 'data' 键是否存在于 data 字典中且其值是否为一个字典
        if 'data' in data and isinstance(data['data'], dict):
            # 提取 'affairsID' 字段
            # 如果 'data' 字典中存在 'affairsID'，则获取其值，否则设为默认空字符串
            affairsID = data['data'].get('affairsID', '')

            # 提取 'infoID' 字段
            # 如果 'data' 字典中存在 'infoID'，则获取其值，否则设为默认空字符串
            infoID = data['data'].get('infoID', '')

            # 提取 'time' 字段
            # 如果 'data' 字典中存在 'time'，则获取其值，否则设为默认空字符串
            time_str = data['data'].get('time', '')
        else:
            # 如果 'data' 键不存在或其值不是字典，则将所有字段设为默认空字符串
            affairsID = ''
            infoID = ''
            time_str = ''

        # 特别处理 'data' 字典内的 'time' 字段
        start_time, end_time = None, None
        if 'to' in time_str:
            start_time_str, end_time_str = time_str.split(' to ')
            start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
            end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S')

        print(start_time, end_time)

        #  这行是操作数据库  todo 之后具体怎么操作库还得改
        #  db_model = OperationLogModel("127.0.0.1", "root", "123456", "assured_deletion")

        request_log = {
            "affairsID": "16881233",
            "userID": "b00001",
            "infoID": "0c1d2e3f4g5h",
            "deleteMethod": "软件删除",
            "deleteGranularity": "age",
            "sourceDomainID": "b1000",
            "timeLimit": "0000000",
            "countLimit": 0
        }
        request_log = {
            "systemID": 0x40000000,
            "systemIP": socket.gethostbyname(socket.gethostname()),
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data": request_log,
            "dataHash": "56e3be093f377b9d984eef02a982d852d1bce062fdb505bcf87df46141fd80aa"
        }


        if infoID and affairsID:
            # 指定的infoID和affairsID，2个日志，非源域的
            # result_json = db_model.get_records_by_infoID_affairsID(infoID, affairsID)
            # # todo 其实，对于删除请求日志，这个永远不会被判断到
            result_json = [request_log]
        elif not infoID:
            # 只有时间段，也是默认源域，5种
            # result_json = db_model.get_records_by_time_period(start_time, end_time)
            result_json = [request_log]
        elif not time_str:
            # 纯infoID，默认此时请求，所有源域的信息，可能有不同的affairsID，5种
            # result_json = db_model.get_records_by_infoID(infoID)
            result_json = [request_log]
        else:
            return jsonify({"error": "wrong request format"}), 500

        # 数据格式精简
        # op_log = db_model.format_log(result_json)

        # 给删除效果评测系统返回的只能是列表
        return jsonify(result_json)

        # filename=infoID+"_"+affairsID

        # # 构建文件路径
        # file_path = os.path.join('log', f"{filename}.json")

        # # 检查文件是否存在
        # if os.path.exists(file_path):
        #     with open(file_path, 'r') as file:
        #         log_data = json.load(file)
        #         return jsonify(log_data)
        # else:
        #     return jsonify({"error": "Log not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 路由：/getTriggerLog
# 功能：根据请求数据获取删除触发日志
# 输入：
#    无（使用 Flask 的 request.get_json() 获取输入数据）
# 输出：
#    JSON - 返回删除请求日志或错误信息
@sendInfo.route('/getTriggerLog', methods=['POST'])
def get_trigger_log():
    try:
        # 从 POST 请求中解析 JSON 数据
        data = request.get_json()
        # 打印接收到的请求信息
        print(data)

        # 解析基本字段
        # 假设 data 是一个字典，包含各种可能的键值对

        # # 检查是否存在 'systemID'，如果存在，则获取 system_id 的值
        # if 'systemID' in data:
        #     system_id = data.get('systemID')  # 系统ID
        #
        # # 检查是否存在 'systemIP'，如果存在，则获取 system_ip 的值
        # if 'systemIP' in data:
        #     system_ip = data.get('systemIP')  # 系统IP地址
        #
        # # 检查是否存在 'mainCMD'，如果存在，则获取 main_cmd 的值
        # if 'mainCMD' in data:
        #     main_cmd = data.get('mainCMD')  # 主命令
        #
        # # 检查是否存在 'subCMD'，如果存在，则获取 sub_cmd 的值
        # if 'subCMD' in data:
        #     sub_cmd = data.get('subCMD')  # 子命令
        #
        # # 检查是否存在 'evidenceID'，如果存在，则获取 evidence_id 的值
        # if 'evidenceID' in data:
        #     evidence_id = data.get('evidenceID')  # 证据ID
        #
        # # 检查是否存在 'msgVersion'，如果存在，则获取 msg_version 的值
        # if 'msgVersion' in data:
        #     msg_version = data.get('msgVersion')  # 消息版本
        #
        # # 检查是否存在 'submittime'，如果存在，则获取 submittime 的值
        # if 'submittime' in data:
        #     submittime = data.get('submittime')  # 提交时间
        #
        # # 检查是否存在 'dataHash'，如果存在，则获取 data_hash 的值
        # if 'dataHash' in data:
        #     data_hash = data.get('dataHash')  # 数据哈希
        #
        # # 检查是否存在 'datasign'，如果存在，则获取 datasign 的值
        # if 'datasign' in data:
        #     datasign = data.get('datasign')  # 数据签名

        # 对infoID的解析
        # 检查 'data' 键是否存在于 data 字典中且其值是否为一个字典
        if 'data' in data and isinstance(data['data'], dict):
            # 提取 'affairsID' 字段
            # 如果 'data' 字典中存在 'affairsID'，则获取其值，否则设为默认空字符串
            affairsID = data['data'].get('affairsID', '')

            # 提取 'infoID' 字段
            # 如果 'data' 字典中存在 'infoID'，则获取其值，否则设为默认空字符串
            infoID = data['data'].get('infoID', '')

            # 提取 'time' 字段
            # 如果 'data' 字典中存在 'time'，则获取其值，否则设为默认空字符串
            time_str = data['data'].get('time', '')
        else:
            # 如果 'data' 键不存在或其值不是字典，则将所有字段设为默认空字符串
            affairsID = ''
            infoID = ''
            time_str = ''

        # 特别处理 'data' 字典内的 'time' 字段
        start_time, end_time = None, None
        if 'to' in time_str:
            start_time_str, end_time_str = time_str.split(' to ')
            start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
            end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S')

        print(start_time, end_time)

        #  这行是操作数据库  todo 之后具体怎么操作库还得改
        #  db_model = OperationLogModel("127.0.0.1", "root", "123456", "assured_deletion")

        trigger_log = {
            "affairsID": "16881233",
            "userID": "b00001",
            "infoID": "0c1d2e3f4g5h",
            "deleteMethod": "软件删除",
            "deleteGranularity": "age",
            "deleteTriggers": "按需触发"   #(按需触发，计时触发，计次触发)
        }
        trigger_log = {
            "systemID": 0x40000000,
            "systemIP": socket.gethostbyname(socket.gethostname()),
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data": trigger_log,
            "dataHash": "56e3be093f377b9d984eef02a982d852d1bce062fdb505bcf87df46141fd80aa"
        }

        if infoID and affairsID:
            # 指定的infoID和affairsID，2个日志，非源域的，
            # # todo 其实，对于删除触发日志，这个永远不会被判断到
            # result_json = db_model.get_records_by_infoID_affairsID(infoID, affairsID)
            result_json = [trigger_log]
        elif not infoID:
            # 只有时间段，也是默认源域，5种
            # result_json = db_model.get_records_by_time_period(start_time, end_time)
            result_json = [trigger_log]
        elif not time_str:
            # 纯infoID，默认此时请求，所有源域的信息，可能有不同的affairsID，5种
            # result_json = db_model.get_records_by_infoID(infoID)
            result_json = [trigger_log]
        else:
            return jsonify({"error": "wrong request format"}), 500

        # 数据格式精简
        # op_log = db_model.format_log(result_json)

        # 给删除效果评测系统返回的只能是列表
        return jsonify(result_json)

        # filename=infoID+"_"+affairsID

        # # 构建文件路径
        # file_path = os.path.join('log', f"{filename}.json")

        # # 检查文件是否存在
        # if os.path.exists(file_path):
        #     with open(file_path, 'r') as file:
        #         log_data = json.load(file)
        #         return jsonify(log_data)
        # else:
        #     return jsonify({"error": "Log not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 路由：/getNotificationLog'
# 功能：根据请求数据获取删除通知日志
# 输入：
#    无（使用 Flask 的 request.get_json() 获取输入数据）
# 输出：
#    JSON - 返回删除请求日志或错误信息
@sendInfo.route('/getNotificationLog', methods=['POST'])
def get_notification_log():
    try:
        # 从 POST 请求中解析 JSON 数据
        data = request.get_json()
        # 打印接收到的请求信息
        print(data)

        # 解析基本字段
        # 假设 data 是一个字典，包含各种可能的键值对

        # # 检查是否存在 'systemID'，如果存在，则获取 system_id 的值
        # if 'systemID' in data:
        #     system_id = data.get('systemID')  # 系统ID
        #
        # # 检查是否存在 'systemIP'，如果存在，则获取 system_ip 的值
        # if 'systemIP' in data:
        #     system_ip = data.get('systemIP')  # 系统IP地址
        #
        # # 检查是否存在 'mainCMD'，如果存在，则获取 main_cmd 的值
        # if 'mainCMD' in data:
        #     main_cmd = data.get('mainCMD')  # 主命令
        #
        # # 检查是否存在 'subCMD'，如果存在，则获取 sub_cmd 的值
        # if 'subCMD' in data:
        #     sub_cmd = data.get('subCMD')  # 子命令
        #
        # # 检查是否存在 'evidenceID'，如果存在，则获取 evidence_id 的值
        # if 'evidenceID' in data:
        #     evidence_id = data.get('evidenceID')  # 证据ID
        #
        # # 检查是否存在 'msgVersion'，如果存在，则获取 msg_version 的值
        # if 'msgVersion' in data:
        #     msg_version = data.get('msgVersion')  # 消息版本
        #
        # # 检查是否存在 'submittime'，如果存在，则获取 submittime 的值
        # if 'submittime' in data:
        #     submittime = data.get('submittime')  # 提交时间
        #
        # # 检查是否存在 'dataHash'，如果存在，则获取 data_hash 的值
        # if 'dataHash' in data:
        #     data_hash = data.get('dataHash')  # 数据哈希
        #
        # # 检查是否存在 'datasign'，如果存在，则获取 datasign 的值
        # if 'datasign' in data:
        #     datasign = data.get('datasign')  # 数据签名

        # 对infoID的解析
        # 检查 'data' 键是否存在于 data 字典中且其值是否为一个字典
        if 'data' in data and isinstance(data['data'], dict):
            # 提取 'affairsID' 字段
            # 如果 'data' 字典中存在 'affairsID'，则获取其值，否则设为默认空字符串
            affairsID = data['data'].get('affairsID', '')

            # 提取 'infoID' 字段
            # 如果 'data' 字典中存在 'infoID'，则获取其值，否则设为默认空字符串
            infoID = data['data'].get('infoID', '')

            # 提取 'time' 字段
            # 如果 'data' 字典中存在 'time'，则获取其值，否则设为默认空字符串
            time_str = data['data'].get('time', '')
        else:
            # 如果 'data' 键不存在或其值不是字典，则将所有字段设为默认空字符串
            affairsID = ''
            infoID = ''
            time_str = ''

        # 特别处理 'data' 字典内的 'time' 字段
        start_time, end_time = None, None
        if 'to' in time_str:
            start_time_str, end_time_str = time_str.split(' to ')
            start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
            end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S')

        print(start_time, end_time)

        #  这行是操作数据库  todo 之后具体怎么操作库还得改
        #  db_model = OperationLogModel("127.0.0.1", "root", "123456", "assured_deletion")

        notification_log = {
            "affairsID": "16881233",
            "userID": "b00001",
            "infoID": "0c1d2e3f4g5h",
            "deleteMethod": "软件删除",
            "deleteGranularity": "age",
            "deleteNotifyTree": {
                "b1000": {
                    "children": [
                        {
                            "b1001": {
                                "children": []
                            }
                        }
                    ]
                }
            }
        }
        notification_log = {
            "systemID": 0x40000000,
            "systemIP": socket.gethostbyname(socket.gethostname()),
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data": notification_log,
            "dataHash": "56e3be093f377b9d984eef02a982d852d1bce062fdb505bcf87df46141fd80aa"
        }


        if infoID and affairsID:
            # 指定的infoID和affairsID，2个日志，非源域的
            # result_json = db_model.get_records_by_infoID_affairsID(infoID, affairsID)
            result_json = [notification_log]
        elif not infoID:
            # 只有时间段，也是默认源域，5种
            # result_json = db_model.get_records_by_time_period(start_time, end_time)
            result_json = [notification_log]
        elif not time_str:
            # 纯infoID，默认此时请求，所有源域的信息，可能有不同的affairsID，5种
            # result_json = db_model.get_records_by_infoID(infoID)
            result_json = [notification_log]
        else:
            return jsonify({"error": "wrong request format"}), 500

        # 数据格式精简
        # op_log = db_model.format_log(result_json)

        # 给删除效果评测系统返回的只能是列表
        return jsonify(result_json)

        # filename=infoID+"_"+affairsID

        # # 构建文件路径
        # file_path = os.path.join('log', f"{filename}.json")

        # # 检查文件是否存在
        # if os.path.exists(file_path):
        #     with open(file_path, 'r') as file:
        #         log_data = json.load(file)
        #         return jsonify(log_data)
        # else:
        #     return jsonify({"error": "Log not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 路由：/getConfirmationLog
# 功能：根据请求数据获取删除确认日志
# 输入：
#    无（使用 Flask 的 request.get_json() 获取输入数据）
# 输出：
#    JSON - 返回删除确认日志或错误信息

@sendInfo.route('/getConfirmationLog', methods=['POST'])
def get_confirmation_log():
    try:
        # 从 POST 请求中解析 JSON 数据
        data = request.get_json()
        # 打印接收到的请求信息
        print(data)

        # 解析基本字段
        # 假设 data 是一个字典，包含各种可能的键值对

        # # 检查是否存在 'systemID'，如果存在，则获取 system_id 的值
        # if 'systemID' in data:
        #     system_id = data.get('systemID')  # 系统ID
        #
        # # 检查是否存在 'systemIP'，如果存在，则获取 system_ip 的值
        # if 'systemIP' in data:
        #     system_ip = data.get('systemIP')  # 系统IP地址
        #
        # # 检查是否存在 'mainCMD'，如果存在，则获取 main_cmd 的值
        # if 'mainCMD' in data:
        #     main_cmd = data.get('mainCMD')  # 主命令
        #
        # # 检查是否存在 'subCMD'，如果存在，则获取 sub_cmd 的值
        # if 'subCMD' in data:
        #     sub_cmd = data.get('subCMD')  # 子命令
        #
        # # 检查是否存在 'evidenceID'，如果存在，则获取 evidence_id 的值
        # if 'evidenceID' in data:
        #     evidence_id = data.get('evidenceID')  # 证据ID
        #
        # # 检查是否存在 'msgVersion'，如果存在，则获取 msg_version 的值
        # if 'msgVersion' in data:
        #     msg_version = data.get('msgVersion')  # 消息版本
        #
        # # 检查是否存在 'submittime'，如果存在，则获取 submittime 的值
        # if 'submittime' in data:
        #     submittime = data.get('submittime')  # 提交时间
        #
        # # 检查是否存在 'dataHash'，如果存在，则获取 data_hash 的值
        # if 'dataHash' in data:
        #     data_hash = data.get('dataHash')  # 数据哈希
        #
        # # 检查是否存在 'datasign'，如果存在，则获取 datasign 的值
        # if 'datasign' in data:
        #     datasign = data.get('datasign')  # 数据签名

        # 对infoID的解析
        # 检查 'data' 键是否存在于 data 字典中且其值是否为一个字典
        if 'data' in data and isinstance(data['data'], dict):
            # 提取 'affairsID' 字段
            # 如果 'data' 字典中存在 'affairsID'，则获取其值，否则设为默认空字符串
            affairsID = data['data'].get('affairsID', '')

            # 提取 'infoID' 字段
            # 如果 'data' 字典中存在 'infoID'，则获取其值，否则设为默认空字符串
            infoID = data['data'].get('infoID', '')

            # 提取 'time' 字段
            # 如果 'data' 字典中存在 'time'，则获取其值，否则设为默认空字符串
            time_str = data['data'].get('time', '')
        else:
            # 如果 'data' 键不存在或其值不是字典，则将所有字段设为默认空字符串
            affairsID = ''
            infoID = ''
            time_str = ''

        # 特别处理 'data' 字典内的 'time' 字段
        start_time, end_time = None, None
        if 'to' in time_str:
            start_time_str, end_time_str = time_str.split(' to ')
            start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
            end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S')

        print(start_time, end_time)

        #  这行是操作数据库  todo 之后具体怎么操作库还得改
        #  db_model = OperationLogModel("127.0.0.1", "root", "123456", "assured_deletion")

        title = "企业节点对信息" + "0c1d2e3f4g5h" + "进行删除通知"
        abstract = f"企业节点" + "b1001"+ "通过" + "按需触发" + "接受" + "用户" + "b100001" + "删除" + "0c1d2e3f4g5h" + "信息的请求,进行删除通知,通知完成"
        # deleteIntention = data[0][0] + "请求删除其身份证信息"
        memorydata = {
            "systemID": 0x40000000,
            "systemIP": socket.gethostbyname(socket.gethostname()),
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data": {
                "affairsID": "16881233",
                "title": title,
                "abstract": abstract,
                "keyWords": "删除通知",
                "category": "4-1-1",
                "userID": "b00001",
                "infoID": "0c1d2e3f4g5h",
                "deleteGranularity": "age",
                "deleteConfirmation": "200",
                "deleteMethod": "软件删除",
                "deleteNotifyTree": {
                    "b1000": {
                        "children": [
                            {
                                "b1001": {
                                    "children": []
                                }
                            }
                        ]
                    }
                },
                "delConfirmSignatureDict": {"b1003": "7d2418d9c03b9374555b140801cf7dfd55b23a12ad15ccf951480f257f29687780847c7608a66db9f7361c23c496fbd5860ccc107779f41b09cbd60f8718b14838d1008e53a3db80f13ebb96db9c85923a70cff0c0e3ec5e299d5687735f61231ec8876ac5272d5404607ef7d2100c6b9bc713056ffe738536b3d71e31b73f4609286f8db16e062e7a2100eb497cad4103afd8e90a28f94898481793d134f339378e19c5c2afe9152ead11da16ac654fad90e0fa59897faf8f6cc9f8d8216d2ddacd1759822735f533f86994f283448dd5edcef766e9ea0aeeab6664c2dad7cc5c4695e9150ce0bf685e122dbb68356e1a328e6b1ee62265bb21dca673684ac1"}
            },
            "dataHash": "56e3be093f377b9d984eef02a982d852d1bce062fdb505bcf87df46141fd80aa",

        }

        if infoID and affairsID:
            # 指定的infoID和affairsID，2个日志，非源域的
            # result_json = db_model.get_records_by_infoID_affairsID(infoID, affairsID)
            result_json = []
        elif not infoID:
            # 只有时间段，也是默认源域，5种
            # result_json = db_model.get_records_by_time_period(start_time, end_time)
            result_json = []
        elif not time_str:
            # 纯infoID，默认此时请求，所有源域的信息，可能有不同的affairsID，5种
            # result_json = db_model.get_records_by_infoID(infoID)
            result_json = []
        else:
            return jsonify({"error": "wrong request format"}), 500

        # 数据格式精简
        # op_log = db_model.format_log(result_json)

        # 给删除效果评测系统返回的只能是列表
        return jsonify(result_json)

        # filename=infoID+"_"+affairsID

        # # 构建文件路径
        # file_path = os.path.join('log', f"{filename}.json")

        # # 检查文件是否存在
        # if os.path.exists(file_path):
        #     with open(file_path, 'r') as file:
        #         log_data = json.load(file)
        #         return jsonify(log_data)
        # else:
        #     return jsonify({"error": "Log not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500





if __name__ == "__main__":
    # sendInfo.run(host='127.0.0.1', port=30000, debug=True)
    sendInfo.run(host='172.18.0.141', port=30000, debug=True)
