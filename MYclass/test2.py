# import asyncio
# 
# import requests
# from flask import Flask, json, jsonify
# from flask import Blueprint
# 
# app2 = Blueprint("app2", __name__)
# async def handle_request_from_user():
#     await asyncio.sleep(2)  # 模拟处理用户请求的耗时操作
#     response = "test2收到用户请求"
#     return jsonify({"response": response})
# 
# async def perform_business_operation():
#     await asyncio.sleep(2)  # 模拟业务操作的耗时操作
#     print("test2执行业务操作")
#     delintention = {
#         "affairs_id": "dengxin",
#         "user_id": "dengxin",
#         "deleteGranularity": "dengxin",
#         "info_id": "dengxin",
#         "source_bus_id": "dengxin",
#         "count_limit": "dengxin",
#         "deleteMethod": "dengxin"
#     }
#     print(delintention)
# 
# @app2.route('/test2', methods=['POST'])
# async def page2():
#     user_task = asyncio.create_task(handle_request_from_user())
#     business_task = asyncio.create_task(perform_business_operation())
# 
#     # 首先响应用户请求
#     user_response = await user_task
# 
#     # 然后执行后续业务操作
#     await business_task
# 
#     return user_response

# import asyncio
#
# async def async_task(num):
#     print(f'Task {num} started')
#     await asyncio.sleep(10)  # 模拟耗时操作，例如网络请求、文件读取等。
#     print(f'Task {num} finished')
#     return num
#
# async def main():
#     tasks = [async_task(i) for i in range(3)]
#     print("Before await")
#
#     print("Test...")
#     done, pending = await asyncio.wait(tasks)
#     print("After await")
#     for finished_task in done:
#         print(f'{finished_task} result: {finished_task.result()}')
#
# # 运行main协程
# asyncio.run(main())
# import asyncio
#
# async def my_coroutine():
#     await asyncio.sleep(10)  # 模拟异步等待操作，如磁盘或网络 I/O
#     return "Result after waiting"
#
# async def main():
#     result = await my_coroutine()  # 挂起 main 协程直到 my_coroutine 完成
#     print(result)  # 打印得到的结果，这里会打印 "Result after waiting"
#
# asyncio.run(main())
# print("Start")

# from flask import Flask, request, jsonify, Blueprint
# import json
# import time
# import threading
#
# from flask import copy_current_request_context
# userroute = Flask(__name__)
# @userroute.route("/test/postx/endpointx", methods=['POST'])
# # POST格式为JSON格式
# def intentionAly():
#     # 通过判断post是否包含time、count字段，来调用DelTrigger中不同的函数
#
#     data = request.json
#     data = json.loads(data)
#
#     def process_task():
#         time.sleep(10)
#         print("测试")
#
#
#     thread = threading.Thread(target=process_task)
#     thread.start()
#     return f"企业节点{1000}接收请求信息成功！"
#
# if __name__ == "__main__":
#      userroute.run(host='127.0.0.1', port= 20000, debug=True)

import configparser
from pprint import pprint
from flask import request, Blueprint, Flask, jsonify
import requests
import json
from InfoMemory import InfoMemory
from Json2Tree import json2tree
import threading
import socket
import datetime
from flask import Response
from io import BytesIO
import json

sendInfo = Flask(__name__)
# todo 每次启动路由，标识当前路由（企业）ID，通过外部标识输入参数
Bus_id = "b1000"

# recvAckDictLock = threading.Lock()        暂时先不考虑竞争关系，删除效果评测系统不会同时发俩个请求
# 专门用于接收来自删除效果评测系统的路由
@sendInfo.route("/result/postx/endpointx", methods=['POST'])
def Logsend():
    loginfo = request.json
    # loginfo = json.loads(loginfo)
    print(f"日志请求信息为：{loginfo}")
    if loginfo is None:
        return jsonify({"error": "Invalid JSON data"}), 400

    # ip = "127.0.0.1"  # 删除效果评测系统开放的ip
    # port = 50000
    # 计划不采用post的方式发送查询结果，直接return的方式返回

    # 创建ConfigParser对象
    config = configparser.ConfigParser()
    # 读取配置文件
    config.read('config.ini')
    # 从配置文件中获取值
    host = config.get('Database', 'host')
    user = config.get('Database', 'user')
    password = config.get('Database', 'password')
    mysqlport = config.getint('Database', 'port')
    database = config.get('Database', 'database_prefix')
    database = database + Bus_id

    loginfo = loginfo["data"]
    # loginfo["userID"] = "b00002"  当时为了和删除效果评测系统模拟测试，给定的一个数值
    if loginfo["getLogType"] == "getDelete_IntentLog":
        # processor = InfoMemory(host=host, user=user, port=mysqlport, password=password, database=database)
        try:
            # data = processor.search_IntentLog(loginfo["affairsID"], loginfo["infoID"])
            intent_log = {
                'affairsID': '16881233',
                'userID': 'b00001',
                'infoID': '0c1d2e3f4g5h',
                'deleteMethod': '软件删除',
                "deleteIntention": 'b00001'+"请求删除其"+'0c1d2e3f4g5h'+"信息",
                'deleteGranularity': 'age',
                "sourceDomainID": "b1000",
                "timeLimit": "0000000",
                "countLimit": 0
            }

            intent_log = {
                    "systemID": 0x40000000,
                    "systemIP": socket.gethostbyname(socket.gethostname()),
                    "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "data": intent_log,
                    "dataHash": "56e3be093f377b9d984eef02a982d852d1bce062fdb505bcf87df46141fd80aa"
            }

            proxy = BytesIO()
            json_str = json.dumps(intent_log)
            json_bytes = json_str.encode('utf-8')  # 编码为UTF-8

            # 将字节写入文件-like对象
            proxy.write(json_bytes)

            # 将JSON数据写入文件-like对象
            # 移动到开始位置，以便发送文件的内容
            proxy.seek(0)

            # 创建一个生成器，从文件-like对象读取并生成响应

            def generate():
                yield from proxy
                proxy.close()  # 关闭文件-like对象

            filename = loginfo["infoID"]+"_"+loginfo["affairsID"]+"_Delete_Intent_log.json"
            # 发送响应
            return Response(generate(), mimetype='application/json',
                            headers={
                                "Content-Disposition": f"attachment;filename={filename}"})
            # 这里json文件的名字需要改
        except Exception as e:
            return (f"数据查询不存在")

    elif loginfo["getLogType"] == "getDelete_RequestLog":
       #  processor = InfoMemory(host=host, user=user, port=mysqlport, password=password, database=database)
        try:
          #  data = processor.search_ReqestLog(loginfo["affairsID"], loginfo["infoID"])
            request_log = {
                'affairsID': '16881233',
                'userID': 'b00001',
                'infoID': '0c1d2e3f4g5h',
                'deleteMethod': '软件删除',
                'deleteGranularity': 'age',
                "sourceDomainID": "b1000",
                "timeLimit": "0000000",
                "countLimit": 0
            }

            request_log = {
                    "systemID": 0x40000000,
                    "systemIP": socket.gethostbyname(socket.gethostname()),
                    "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "data": request_log,
                    "dataHash": "56e3be093f377b9d984eef02a982d852d1bce062fdb505bcf87df46141fd80aa"
            }

            proxy = BytesIO()
            json_str = json.dumps(request_log)
            json_bytes = json_str.encode('utf-8')  # 编码为UTF-8

            # 将字节写入文件-like对象
            proxy.write(json_bytes)

            # 将JSON数据写入文件-like对象
            # 移动到开始位置，以便发送文件的内容
            proxy.seek(0)

            # 创建一个生成器，从文件-like对象读取并生成响应

            def generate():
                yield from proxy
                proxy.close()  # 关闭文件-like对象

            filename = loginfo["infoID"]+"_"+loginfo["affairsID"]+"_Delete_Request_log.json"
            # 发送响应
            return Response(generate(), mimetype='application/json',
                            headers={
                                "Content-Disposition": f"attachment;filename={filename}"})

        except Exception as e:
            return(f"数据查询不存在")

    elif loginfo["getLogType"] == "getDelete_TriggerLog":
        # processor = InfoMemory(host=host, user=user, port=mysqlport, password=password, database=database)
        try:   # 已经改到这里
          #  data = processor.search_TriggerLog(loginfo["affairsID"], loginfo["infoID"])
            trigger_log = {
                'affairsID': '16881233',
                'userID': 'b00001',
                'infoID': '0c1d2e3f4g5h',
                'deleteMethod': '软件删除',
                'deleteGranularity': 'age',
                "deleteTriggers": "按需触发",
            }


            trigger_log = {
                    "systemID": 0x40000000,
                    "systemIP": socket.gethostbyname(socket.gethostname()),
                    "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "data": trigger_log,
                    "dataHash": "56e3be093f377b9d984eef02a982d852d1bce062fdb505bcf87df46141fd80aa"
            }

            proxy = BytesIO()
            json_str = json.dumps(trigger_log)
            json_bytes = json_str.encode('utf-8')  # 编码为UTF-8

            # 将字节写入文件-like对象
            proxy.write(json_bytes)

            # 将JSON数据写入文件-like对象
            # 移动到开始位置，以便发送文件的内容
            proxy.seek(0)
            # 创建一个生成器，从文件-like对象读取并生成响应

            def generate():
                yield from proxy
                proxy.close()  # 关闭文件-like对象

            filename = loginfo["infoID"]+"_"+loginfo["affairsID"]+"_Delete_Trigger_log.json"
            # 发送响应
            return Response(generate(), mimetype='application/json',
                            headers={"Content-Disposition": f"attachment;filename={filename}"})

        except Exception as e:
            return(f"数据查询不存在")

    elif loginfo["getLogType"] == "getDelete_NotificationLog":
        # processor = InfoMemory(host=host, user=user, port=mysqlport, password=password, database=database)
        try:
          #  data = processor.search_notifyLog(loginfo["affairsID"], loginfo["infoID"])
            notification_log = {
                'affairsID': '16881233',
                'userID': 'b00001',
                'infoID': '0c1d2e3f4g5h',
                'deleteMethod': '软件删除',
                'deleteGranularity': 'age',
                'deleteNotifyTree': '{"b1000": {"children": [{"b1001": {"children": '
                                    '["b1002"]}}, {"b1003": {"children": '
                                    '["b1004"]}}]}}',
            }

            notification_log = {
                    "systemID": 0x40000000,
                    "systemIP": socket.gethostbyname(socket.gethostname()),
                    "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "data": notification_log,
                    "dataHash": "56e3be093f377b9d984eef02a982d852d1bce062fdb505bcf87df46141fd80aa"
            }

            proxy = BytesIO()
            json_str = json.dumps(notification_log)
            json_bytes = json_str.encode('utf-8')  # 编码为UTF-8

            # 将字节写入文件-like对象
            proxy.write(json_bytes)

            # 将JSON数据写入文件-like对象
            # 移动到开始位置，以便发送文件的内容
            proxy.seek(0)
            # 创建一个生成器，从文件-like对象读取并生成响应

            def generate():
                yield from proxy
                proxy.close()  # 关闭文件-like对象

            filename = loginfo["infoID"]+"_"+loginfo["affairsID"]+"_Delete_Notification_log.json"
            # 发送响应
            return Response(generate(), mimetype='application/json',
                            headers={"Content-Disposition": f"attachment;filename={filename}"})

        except Exception as e:
            return(f"数据查询不存在")

    elif loginfo["getLogType"] == "getDelete_ConfirmationLog":

       # processor = InfoMemory(host=host, user=user, port=mysqlport, password=password, database=database)
        # data = processor.searchinfoall(loginfo["userID"], loginfo["infoID"])
        try:
            # data = processor.searchinfoall(loginfo["userID"], loginfo["infoID"])
          #  data = processor.search_confirmLog(loginfo["affairsID"], loginfo["infoID"])
            title = "企业节点对信息" + loginfo["infoID"] + "进行删除通知"
            abstract = f"企业节点" + "b1000"+ "通过" + 'b00001' + "接受" + "用户" + 'b00001'+ "删除" + 'b00001' + "信息的请求,进行删除通知,通知完成"
            # deleteIntention = data[0][0] + "请求删除其身份证信息"
            memorydata = {
                "systemID": 0x40000000,
                "systemIP": socket.gethostbyname(socket.gethostname()),
                "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'data': {
                    'abstract': '企业节点b1000通过按需触发接受用户b00001删除0c1d2e3f4g5h信息的请求,进行删除通知,通知完成',
                    'affairsID': '16881233',
                    'category': '4-1-1',
                    'delConfirmSignatureDict': '{"b1003": '
                                               '"7d2418d9c03b9374555b140801cf7dfd55b23a12ad15ccf951480f257f29687780847c7608a66db9f7361c23c496fbd5860ccc107779f41b09cbd60f8718b14838d1008e53a3db80f13ebb96db9c85923a70cff0c0e3ec5e299d5687735f61231ec8876ac5272d5404607ef7d2100c6b9bc713056ffe738536b3d71e31b73f4609286f8db16e062e7a2100eb497cad4103afd8e90a28f94898481793d134f339378e19c5c2afe9152ead11da16ac654fad90e0fa59897faf8f6cc9f8d8216d2ddacd1759822735f533f86994f283448dd5edcef766e9ea0aeeab6664c2dad7cc5c4695e9150ce0bf685e122dbb68356e1a328e6b1ee62265bb21dca673684ac1", '
                                               '"b1004": '
                                               '"7dcad5848cab643231d56e9f78667e6fc5adad6768eba2d5ebade67bbb133b2924bf169c0637ef5d1015bc1ce378f9015742980e8d3b96bdae9b808d6f0328edd199a3e9c27e9a971c230a3d8bf17f93294cd6f6ceb4e8c0ec33ff36e984e6c7ae02880bdcb505993f60b97dd6c0243d8531f45d7d9a053e4241c9113ffd79dd75c4c306c2c0561d1dab86d591e2ae3d050e68ff1b228bfa0317a81fe7bf23274e58a69d680c7d3817de6495297f94fd01abb5f407bc62f19730d8273c30c45fc0ec42be0079f746cbe5c0f4b88e18e3482529edb11b4892b889801905baf15f362e471570b4a1ed2b37666dc66897daca589785856e41a16d2035dcbd42764b", '
                                               '"b1001": '
                                               '"21f3690bbd0e5ce08134cbdd65020dce2d23ab04bb859d5b59793df490d8391c1212453b7e1326285596abdd9670f8c57787f7bebe2aa78bf66b3ca0b970d0189c204fbbdfda138d7382f86ac12f2cb078db056b423dd086e9c7d8da9b88bf17582d783a32662353a7c4d16309999cd0684f6a51d308b2dbd00aa5865ab7f4463cadfef0fd738dc0869c4c76c21c3f954e8c0b44695cf2faf34bebab1dbb1d6eef88102f86276c843432f885584c5e67eb1c4913c839ee77fabc5e124a5ddbff2698bf8b6b1afd964edebfd2c8af67b6cbfa3999c0a105c7805c626e20d3a63ddb7c56c7973955c09ce7d51c1af91b2a43150555652849271c3f3f21e9042145", '
                                               '"b1002": '
                                               '"c9d3948cb9f242e65c6c3d2f76b2aea49580e0e923655ad01622f0ddf07782301766c3a4ab4445f8cc5e0680661f7fe33ed54da6a5fbf8127000b9ce52450d8593b4f731f412dfe615475f3cfd8beeb9851dc6dae558d83059c5642940ac13944decc07beeb1822d5595cb38a6f59f5bab00e9e76dbe0a0f157f3b8575c44d01cebdbe652827535f47bd6d365cdabff5a55dd0438b34458bc596a39afb45b5e8de94403caf51aa2cf961af2a24adeea011b3063723c175f4cd76f95e8b1c0eacb887c2159f311c599d5c5424b19b6dd15f079fc5f3574b256bc871e9d041639f57550cbf466ec2133b097f9431ab50c6978ed44a4d37523d6a3771db32ed8671"}',
                    'deleteConfirmation': '200',
                    'deleteGranularity': 'age',
                    'deleteMethod': '软件删除',
                    'deleteNotifyTree': '{"b1000": {"children": [{"b1001": {"children": '
                                        '["b1002"]}}, {"b1003": {"children": '
                                        '["b1004"]}}]}}',
                    'infoID': '0c1d2e3f4g5h',
                    'keyWords': '删除通知',
                    'title': '企业节点对信息0c1d2e3f4g5h进行删除通知',
                    'userID': 'b00001'
                },
                "dataHash": "56e3be093f377b9d984eef02a982d852d1bce062fdb505bcf87df46141fd80aa",
            }

            # 在内存中创建一个文件-like对象
            proxy = BytesIO()
            json_str = json.dumps(memorydata)
            json_bytes = json_str.encode('utf-8')  # 编码为UTF-8

            # 将字节写入文件-like对象
            proxy.write(json_bytes)

            # 将JSON数据写入文件-like对象
            # 移动到开始位置，以便发送文件的内容
            proxy.seek(0)
            # 创建一个生成器，从文件-like对象读取并生成响应

            def generate():
                yield from proxy
                proxy.close()  # 关闭文件-like对象

            filename = loginfo["infoID"]+"_"+loginfo["affairsID"]+"_Delete_Confirmation_log.json"
            # 发送响应
            return Response(generate(), mimetype='application/json',
                            headers={"Content-Disposition": f"attachment;filename={filename}"})

        except Exception as e:
            print(e)
            return(f"数据查询不存在")

    else:
        print("请求数据错误！")

    return "删除效果评测系统推送测试成功！"


if __name__ == "__main__":
    # sendInfo.run(host='127.0.0.1', port=30000, debug=True)
    sendInfo.run(host='192.168.43.48', port=30000, debug=True)

