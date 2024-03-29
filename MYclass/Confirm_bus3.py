import time

import cryptography
import httpx
from flask import Flask, request, jsonify, Blueprint
from MYclass.ConnectSysDel import ConnectSysDel
from MYclass.DelTrigger import DelTrigger
import ConnectOne
import asynfunction
import asyncio
import requests
import json
import hashlib
import csv
import threading
from MYclass import DelNotifyOther, SignAndKey
from MYclass.Json2Tree import json2tree
from MYclass.PathSelect import PathSelect, TreeParentFinder
import datetime
import pprint
# 辅助函数
def print_with_timestamp(message):
    current_time = datetime.datetime.now()
    timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")
# 用于记录已经接收到的删除确认个数
recvAckDict = {
   # "affairs_id": [2, {"bx1000": "0xasdas"}, {"bx1001": "0xasdfas"}]
}

# todo 每次启动路由，标识当前路由（企业）ID，通过外部标识输入参数
Bus_id = "b1003"
confirm3 = Blueprint("confirm3", __name__)
recvAckDictLock = threading.Lock()
# 专门用于接收后继节点传输的删除确认的路由
@confirm3.route("/confirm/postx/endpointx", methods=['POST'])
def delConfirmAcc():
    # 这里接收到的信息是发回的删除通知确认
    # DelConfirm = {
    #     "affairs_id": delNotice["affairs_id"],
    #     "from_bus_id": Bus_id,
    #     "to_bus_id": node,
    #     "user_id": delNotice["user_id"],
    #     "info_id": delNotice["info_id"],
    #     "deleteNotifyTree": delNotice["deleteNotifyTree"],
    #     "DelConfirmSignatureDict": {Bus_id: signature}
    # }
    DelConfirm_1 = request.json
    DelConfirm_1 = json.loads(DelConfirm_1)

    tree = json2tree(DelConfirm_1["deleteNotifyTree"])
    node = [i._identifier for i in tree.children(Bus_id)]
    childrencount = len(node)
    print_with_timestamp(f"本企业{Bus_id}对于本条信息的'子节点企业'为{node}")

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
        if SignAndKey.verify_signature(public_key, hash_result, bytes.fromhex(
                DelConfirm_1["DelConfirmSignatureDict"][DelConfirm_1["from_bus_id"]])):
            print_with_timestamp(f"本次收到来自企业{DelConfirm_1['from_bus_id']}签名验证成功，消息未被篡改")
        else:
            print_with_timestamp(f"本次收到来自企业{DelConfirm_1['from_bus_id']}签名验证成功，消息未被篡改")

        # 现在通过比较 子节点个数和recvAckDict[affairs_id]值是否相等
        if childrencount != recvAckDict[DelConfirm_1["affairs_id"]][0]:

            print_with_timestamp(
                f"本企业{Bus_id}对于本条信息的'子节点企业'个数为{childrencount},已经收到的删除通知确认个数为{recvAckDict[DelConfirm_1['affairs_id']][0]},二者不相等，继续等待···")
            print_with_timestamp("已经收到的删除通知确认信息内容如下：")
            pprint.pprint(recvAckDict)
            # sign = {}
            # for item in recvAckDict[DelConfirm_1["affairs_id"]][1:]:
            #     sign.update(item)
            # receive = len(sign)
            # print(receive)
            # num = tree.__len__() - 1
            # print("删除通知成功率：", receive / num)
            return "对方已成功接收到删除通知确认！"
        else:
            # 生成自己的签名
            print_with_timestamp(
                f"本企业{Bus_id}对于本条信息的'子节点企业'个数为{childrencount},已经收到的删除通知确认个数为{recvAckDict[DelConfirm_1['affairs_id']][0]},二者相等，继续执行后续操作")
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
                        print_with_timestamp(f"给'子节点'企业发送删除通知确认成功!")
                        # print_with_timestamp("响应状态码: " + str(response.status_code))
                        break  # 如果成功，跳出循环
                    else:
                        print_with_timestamp(f"给'子节点'企业发送删除通知确认失败!")
                        print_with_timestamp("响应状态码: " + str(response.status_code))
                # 循环完仍未成功
                else:
                    print_with_timestamp("循环发送请求达到最大重试次数，仍未成功！")
                return "对方已成功接收到删除通知确认！"

            else:
                # 表示自己是源节点的，没有父节点
                print_with_timestamp(f"删除通知确认已全部验证完毕!")
                # 计算删除成功率
                sign = {}
                for item in recvAckDict[DelConfirm_1["affairs_id"]][1:]:
                    sign.update(item)
                receive = len(sign)
                num = tree.__len__() - 1
                print_with_timestamp(f"本次删除通知的删除通知成功率为:{receive / num}")

                # 此时开始在数据库中存储存证信息
                print_with_timestamp(f"开始存证本地的签名等一系列信息····")
                sign = {
                }
                for item in recvAckDict[DelConfirm_1["affairs_id"]][1:]:
                    sign.update(item)
                sign = json.dumps(sign)
                # todo 换数据库修改此处
                # processor = InfoMemory(host="localhost", user="root", port=3306, password="123456",database="project26")
                # processor = InfoMemory(host="10.170.42.45", port=3306, user="myuser", password="mypassword", database="project26")
                # processor.insert_newrecord(DelConfirm_1["user_id"],sign,DelConfirm_1["info_id"])
                print_with_timestamp(f"本地存证信息已经全部存证结束!")
                recvAckDict.clear()
                return "对方已成功接收到删除通知确认！"

# if __name__ == "__main__":
#     confirm1.run(host='0.0.0.0', port=30001, debug=True)
