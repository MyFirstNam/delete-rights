import configparser
import time

from flask import Flask, request, jsonify, Blueprint
import pprint
import asynfunction
import asyncio
import requests
import json
import hashlib
import csv
import DelNotifyOther, SignAndKey
from InfoMemory import InfoMemory
from Json2Tree import json2tree
from DelIntentionAly import DellntentionAly
import threading
import datetime
import pprint
from HMACverify import verify_hmac
from flask import copy_current_request_context

def print_with_timestamp(message):
    current_time = datetime.datetime.now()
    timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


# todo 每次启动路由，标识当前路由（企业）ID，通过外部标识输入参数
Bus_id = "b1003"

# 处理删除意图or删除通知的的路由及其视图函数
userroute = Flask(__name__)
@userroute.route("/test/postx/endpointx", methods=['POST'])
# POST格式为JSON格式
def intentionAly():
    # 通过判断post是否包含time、count字段，来调用DelTrigger中不同的函数
    # todo 返回一个bool值表示直接的后继节点是否受到删除通知
    # data = request.json
    # data = json.loads(data)

    @copy_current_request_context
    def process_task():
        data = request.json
        data = json.loads(data)
        if "deleteNotifyTree" not in data:
            print_with_timestamp("通过对接收到的信息内容判断，接收到的信息内容为删除意图，执行删除意图解析等一系列操作")
            print_with_timestamp("——————————————————————————————删除意图解析——————————————————————————————")
            delintention = DellntentionAly(data, Bus_id)
            delNotice = delintention.Intention()
        elif "deleteNotifyTree" in data:
            print_with_timestamp("通过对接收到的信息内容判断，接收到的信息内容为删除通知，执行通知转发等一系列操作")
            print_with_timestamp(f'本企业{Bus_id}已经成功接收得到来自于上一跳删除通知')
            print_with_timestamp("——————————————————————————————删除通知验证——————————————————————————————")
            delNotice = data
            # 从请求头中获取消息验证码
            received_hmac = request.headers.get('HMAC')

            with open('keyserect.CSV', 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row['ID'] == delNotice["from_bus_id"]:
                        secret_key = row['Serect']
            # 验证消息验证码
            is_valid = verify_hmac(json.dumps(delNotice), secret_key, received_hmac)
            if is_valid:
                print_with_timestamp("对接收到的删除通知验证成功！")
            else:
                print_with_timestamp("对接收到的删除通知验证失败！")
                return "接收到的删除通知信息已被篡改，请重新发送···"
        else:
            print_with_timestamp("通过对接收到的信息内容判断,未能判断当前信息类型，无法进行后续操作！")

        # 第一个异步函数负责下发删除通知
        # 调用 asynfunction.py 中的异步函数,异步函数负责实现除去返回删除通知应答的所有功能
        # 第二个异步函数返回删除通知应答
        async def delresponse(data):
            # 生成删除通知应答
            tree = json2tree(data["deleteNotifyTree"])
            node = tree.parent(Bus_id)
            DelNoticeResponse = {
                "affairs_id": data["affairs_id"],
                "from_bus_id": Bus_id,
                "to_bus_id": node,
                "user_id": data["user_id"],
                "info_id": data["info_id"],
                "isReceive": True,
            }
            # todo run app.py
            url = "http://127.0.0.1:20098/update_notify"
            data_notify = {"node_id": Bus_id}
            json_data = json.dumps(data_notify)
            time.sleep(4)
            response = requests.post(url, json=json_data)
            if response.status_code == 200:
                print_with_timestamp("删除通知成功！")
            else:
                print_with_timestamp("删除通知失败！")
            print_with_timestamp(f"本企业{Bus_id}已经成功响应！（预留可视化模块接口）")

        task_list = [asynfunction.processNotify(delNotice, Bus_id), delresponse(delNotice)]
        asyncio.run(asyncio.wait(task_list))

    # 使用线程来运行耗时操作
    thread = threading.Thread(target=process_task)
    thread.start()
    # 立即响应客户端
    return f"企业节点{Bus_id}接收请求信息成功！"


recvAckDict = {}
recvAckDictLock = threading.Lock()
@userroute.route("/confirm/postx/endpointx", methods=['POST'])
def delConfirmAcc():
    # 这里接收到的信息是发回的删除通知确认

    DelConfirm_1 = request.json
    DelConfirm_1 = json.loads(DelConfirm_1)
    print_with_timestamp("——————————————————————————————删除通知确认接收——————————————————————————————")
    tree = json2tree(DelConfirm_1["deleteNotifyTree"])
    node = [i._identifier for i in tree.children(Bus_id)]
    childrencount = len(node)
    print_with_timestamp(f'本企业{Bus_id}对于本条信息的"子节点企业"为{DelConfirm_1["from_bus_id"]}')

    # 通过删除通知确认中的删除流转路径查询自己有几个子节点，之后通过根据affairs_id查看recvAckDict全局变量是否达到子节点个数
    with recvAckDictLock:
        if DelConfirm_1["affairs_id"] not in recvAckDict:
            # （1）查询不到，插入一项affairs_id;1,同时只需要保留签名即可
                recvAckDict[DelConfirm_1["affairs_id"]] = [1, DelConfirm_1["DelConfirmSignatureDict"]]
        else:
            # (2) 查询到了，则将affairs_id对应的值加1
                recvAckDict[DelConfirm_1["affairs_id"]][0] = recvAckDict[DelConfirm_1["affairs_id"]][0] + 1
                recvAckDict[DelConfirm_1["affairs_id"]].append(DelConfirm_1["DelConfirmSignatureDict"])

        delconfirmstr = {
            "affairs_id": DelConfirm_1["affairs_id"],
            "from_bus_id": DelConfirm_1["from_bus_id"],
            "to_bus_id": DelConfirm_1["to_bus_id"],
            "user_id": DelConfirm_1["user_id"],
            "info_id": DelConfirm_1["info_id"],
            "deleteNotifyTree": DelConfirm_1["deleteNotifyTree"],
        }

        delconfirmstr = json.dumps(delconfirmstr)
        hash_object = hashlib.sha256()
        hash_object.update(delconfirmstr.encode("utf-8"))
        hash_result = hash_object.digest()

        csv_filename = "key_pairs.csv"
        public_key = SignAndKey.query_Publickey_pair_by_id(csv_filename, DelConfirm_1["from_bus_id"])
        if SignAndKey.verify_signature(public_key, hash_result, bytes.fromhex(DelConfirm_1["DelConfirmSignatureDict"][DelConfirm_1["from_bus_id"]])):
            print_with_timestamp(f"本次收到来自企业{DelConfirm_1['from_bus_id']}签名验证成功，消息未被篡改")
        else:
            print_with_timestamp(f"本次收到来自企业{DelConfirm_1['from_bus_id']}签名验证成功，消息未被篡改")

        # 现在通过比较 子节点个数和recvAckDict[affairs_id]值是否相等
        if childrencount != recvAckDict[DelConfirm_1["affairs_id"]][0]:

            print_with_timestamp(f"本企业{Bus_id}对于本条信息的'子节点企业'个数为{childrencount},已经收到的删除通知确认个数为{recvAckDict[DelConfirm_1['affairs_id']][0]},二者不相等，继续等待···")
            print_with_timestamp("已经收到的删除通知确认信息内容如下：")
            pprint.pprint(recvAckDict)
            return "对方已成功接收到删除通知确认！"
        else:
            # 生成自己的签名
            print_with_timestamp(f"本企业{Bus_id}对于本条信息的'子节点企业'个数为{childrencount},已经收到的删除通知确认个数为{recvAckDict[DelConfirm_1['affairs_id']][0]},二者相等，继续执行后续操作")
            csv_filename = "key_pairs.csv"
            private_key_pem = SignAndKey.query_Privatekey_pair_by_id(csv_filename, Bus_id)
            tree = json2tree(DelConfirm_1["deleteNotifyTree"])
            node = tree.parent(Bus_id)
            if node is not None:
                # node是父节点
                # 寻找到自己节点的父节点，然后就可以发送信息了
                node = node._identifier
                print_with_timestamp(f"本企业{Bus_id}对于本条信息的'父节点企业'为{node}")
                delconfirmstr = {
                    "affairs_id": DelConfirm_1["affairs_id"],
                    "from_bus_id": Bus_id,
                    "to_bus_id": node,
                    "user_id": DelConfirm_1["user_id"],
                    "info_id": DelConfirm_1["info_id"],
                    "deleteNotifyTree": DelConfirm_1["deleteNotifyTree"],
                }
                print_with_timestamp("—————————————————————————————删除通知确认生成与回送—————————————————————————————")
                delconfirmstr = json.dumps(delconfirmstr)
                hash_object = hashlib.sha256()
                hash_object.update(delconfirmstr.encode("utf-8"))
                hash_result = hash_object.digest()
                signature = SignAndKey.sign_message(private_key_pem, hash_result)

                sign = {
                    Bus_id: signature
                }
                for item in recvAckDict[DelConfirm_1["affairs_id"]][1:]:
                    sign.update(item)

                DelConfirm = {
                    "affairs_id": DelConfirm_1["affairs_id"],  # 事务ID
                    "from_bus_id": Bus_id,  # 本节点ID
                    "to_bus_id": node,  # 父节点ID
                    "user_id": DelConfirm_1["user_id"],
                    "info_id": DelConfirm_1["info_id"],
                    "deleteNotifyTree": DelConfirm_1["deleteNotifyTree"],
                   # "DelConfirmSignatureDict": {Bus_id: signature}  # string bus_id: string signature的集合
                    "DelConfirmSignatureDict": sign
                }

                print_with_timestamp(f"本企业{Bus_id}对于本条信息的签名信息已生成！")
                # 把签名信息转成十六进制
                hex_string = DelConfirm["DelConfirmSignatureDict"][Bus_id].hex()
                DelConfirm["DelConfirmSignatureDict"][Bus_id] = hex_string
                DelConfirm = json.dumps(DelConfirm)

                # 此处的ip和port应该通过父节点的ID去查找
                with open('ID.csv', 'r') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        if row['ID'] == node:
                            port = row['port']
                            ip = row['IP']
                # todo 在此处进行删除通知确认异常上报
                url = f"http://{ip}:{port}/confirm/postx/endpointx"
                max_retries = 3  # 最大重试次数
                for _ in range(max_retries):
                    response = requests.post(url, json=DelConfirm)
                    print_with_timestamp(f'发送删除通知确认的网络路径为：{url}')
                    # 检查响应
                    if response.status_code == 200:
                        print_with_timestamp(f"给'父节点'企业发送删除通知确认成功!")
                        # print_with_timestamp("响应状态码: " + str(response.status_code))
                        break  # 如果成功，跳出循环
                    else:
                        print_with_timestamp(f"给'父节点'企业发送删除通知确认成功!")
                        print_with_timestamp("响应状态码: " + str(response.status_code))
                # 循环完仍未成功
                else:
                    print_with_timestamp("循环发送请求达到最大重试次数，仍未成功！")

                if DelConfirm_1["affairs_id"] in recvAckDict:
                    del recvAckDict[DelConfirm_1["affairs_id"]]

                return "对方已成功接收到删除通知确认！"

            else:
                #表示自己是源节点的，没有父节点
                print_with_timestamp(f"删除通知确认已全部验证完毕!")
                # 计算删除成功率
                sign = {}
                for item in recvAckDict[DelConfirm_1["affairs_id"]][1:]:
                    sign.update(item)
                receive = len(sign)
                num = tree.__len__()-1
                # print_with_timestamp(f"本次删除通知的删除通知成功率为:{receive/num}")

                # 此时开始在数据库中存储存证信息
                print_with_timestamp(f"开始存证本地的签名等一系列信息····")
                sign = {
                }
                for item in recvAckDict[DelConfirm_1["affairs_id"]][1:]:
                    sign.update(item)
                sign = json.dumps(sign)

                # 创建ConfigParser对象
                config = configparser.ConfigParser()
                # 读取配置文件
                config.read('config.ini')
                # 从配置文件中获取值
                host = config.get('Database', 'host')
                user = config.get('Database', 'user')
                password = config.get('Database', 'password')
                port = config.getint('Database', 'port')
                database = config.get('Database', 'database_prefix')
                database = database + Bus_id

                processor = InfoMemory(host=host, user=user, port=port, password=password, database=database)
                # processor = InfoMemory(host="10.170.42.45", port=3306, user="myuser", password="mypassword", database="project26")
                processor.insert_newrecord(DelConfirm_1["affairs_id"],sign,DelConfirm_1["info_id"])
                print_with_timestamp(f"本地存证信息已经全部存证结束!")
                if DelConfirm_1["affairs_id"] in recvAckDict:
                    del recvAckDict[DelConfirm_1["affairs_id"]]

                with open('UserIP.csv', 'r') as csvfile:
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        if row['UserID'] == DelConfirm_1["user_id"]:
                            port = row['port']
                            ip = row['IP']

                information = f'请求删除的数据{DelConfirm_1["info_id"]}已经全部通知删除完毕'
                try:
                    url = f"http://{ip}:{port}/user/postx/endpointx"
                    response = requests.post(url, json=information)
                    # 检查响应
                    if response.status_code == 200:
                        return ""
                    else:
                        print_with_timestamp("给用户返回删除通知确认信息时出错！")
                except requests.exceptions.RequestException as e:
                    # 处理请求异常
                    print_with_timestamp(f"发送请求时发生异常: {e}")
                except Exception as e:
                    # 处理其他异常
                    print_with_timestamp(f"发生未知异常: {e}")

                return "对方已成功接收到删除通知确认！"




if __name__ == "__main__":
    # userroute.register_blueprint(route)
    # userroute.register_blueprint(confirm)
    userroute.run(host='127.0.0.1', port=20003, debug=True)
    # userroute.run(host='127.0.0.1', port=int(sys.argv[2]), debug=True)
    # userroute.run(host='127.0.0.1', port= 20001, debug=True)