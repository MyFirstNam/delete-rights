import threading
from flask import Flask, request
import asynfunction
import asyncio
import requests
import json
import hashlib
import csv
import DelNotifyOther, SignAndKey
from Json2Tree import json2tree
#route1 = Blueprint("userroute1", __name__)
# 用于记录已经接收到的删除确认个数
recvAckDict = {
   # "affairs_id": [2, {"bx1000": "0xasdas"}, {"bx1001": "0xasdfas"}]
}

# Bus_id = sys.argv[1]
Bus_id = "b1001"
userroute = Flask(__name__)
@userroute.route("/test/postx/endpointx", methods=['POST'])
def notifyAcc():
    delNotice = request.json  # data已经是一个字典，接收到的是删除通知
    delNotice = json.loads(delNotice)
    print("本节点"+Bus_id+"收到信息")
    # 第一个异步函数负责下发删除通知
    # 调用 asynfunction.py 中的异步函数,异步函数负责实现除去返回删除通知应答的所有功能
    #asynfunction.processNotify(delNotice, Bus_id)
    #这里不需要执行异步函数了，后续的列表中直接执行

    # 第二个异步函数返回删除通知应答
    async def delresponse(data):
        # 生成删除通知应答
        tree = json2tree(delNotice["deleteNotifyTree"])
        # node = tree.parent(Bus_id)._identifier
        node = tree.parent(Bus_id)
        DelNoticeResponse = {
            "affairs_id": data["affairs_id"],
            "from_bus_id": Bus_id,
            "to_bus_id": node,
            "user_id": data["user_id"],
            "info_id": data["info_id"],
            "isReceive": True,
        }
        print("删除通知应答响应成功！")
        print("本节点"+Bus_id+"父节点是：", node)
        #todo 删除通知应答问题怎么办？？？？？
        # 发送删除通知应答，查询发送端的IP和port
        # ip = "202.202.202.20"
        # port = 10001
        # # 把字典格式转为JSON
        # DelResponse = json.dumps(DelNoticeResponse)
        # url = f"http://{ip}:{port}/your/post/endpoint"  # 替换为自己的实际目标URL
        # response = requests.post(url, json=DelResponse)
        # # 检查响应
        # if response.status_code == 200:
        #     print("POST请求成功")
        #     print("响应内容:", response.text)
        # else:
        #     print("POST请求失败")
        #     print("响应状态码:", response.status_code)

    task_list = [asynfunction.processNotify(delNotice, Bus_id), delresponse(delNotice)]
    asyncio.run(asyncio.wait(task_list))
    return "接收成功！"


recvAckDictLock = threading.Lock()
@userroute.route("/confirm/postx/endpointx", methods=['POST'])
def delConfirmAcc():
    # 这里接收到的信息是发回的删除通知确认
    # DelConfirm_1= {
    #     "affairs_id": "",
    #     "from_bus_id": "",
    #     "to_bus_id": "",
    #     "user_id": "",
    #     "info_id": "",
    #     "DataTransferPath_path": "",
    #     "DelConfirmSignatureDict":  {"bx1000":"0xasdas"}  # string bus_id: string signature的集合
    # }
    DelConfirm_1 = request.json
    DelConfirm_1 = json.loads(DelConfirm_1)

    # DataTransferPath_path: {
    #     "b1000": {
    #         "children": [{"b1001":
    #                           {"children":
    #                                ["b1002"]
    #                            }
    #                       },
    #                      {"b1003":
    #                           {"children":
    #                                ["b1004"]
    #                            }
    #                       }]
    #     }
    # }
    # getnextNode = PathSelect(DelConfirm_1["DataTransferPath_path"])
    # nextnode = getnextNode.find_node_and_children(Bus_id)  # 负责根据当前节点，寻找下一个节点,返回一个list,用来查询自己有几个子节点
    # keys_list = []
    # for dictionary in nextnode:  # 字符串转换
    #     for key in dictionary.keys():
    #         keys_list.append(key)
    #
    tree = json2tree(DelConfirm_1["DataTransferPath_path"])
    node = [i._identifier for i in tree.children(Bus_id)]
    childrencount = len(node)
    print("本节点子节点为：", node)
    with recvAckDictLock:
        # 通过删除通知确认中的删除流转路径查询自己有几个子节点，之后通过根据affairs_id查看recvAckDict全局变量是否达到子节点个数
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
            "DataTransferPath_path": DelConfirm_1["DataTransferPath_path"],
        }

        delconfirmstr = json.dumps(delconfirmstr)
        hash_object = hashlib.sha256()
        hash_object.update(delconfirmstr.encode("utf-8"))
        hash_result = hash_object.digest()

        csv_filename = "key_pairs.csv"
        public_key = SignAndKey.query_Publickey_pair_by_id(csv_filename, DelConfirm_1["from_bus_id"])

        if SignAndKey.verify_signature(public_key, hash_result, bytes.fromhex(DelConfirm_1["DelConfirmSignatureDict"][DelConfirm_1["from_bus_id"]])):
            print("签名验证成功，消息未被篡改。")
        else:
            print("签名验证失败，消息可能已被篡改。")

        # 现在通过比较 子节点个数和recvAckDict[affairs_id]值是否相等
        if childrencount != recvAckDict[DelConfirm_1["affairs_id"]][0]:
            print("测试不相等")
            return "确认数不等于子节点数！"
        else:
            # 生成自己的签名
            print("测试相等")
            csv_filename = "key_pairs.csv"
            private_key_pem = SignAndKey.query_Privatekey_pair_by_id(csv_filename, Bus_id)
            # parentnode = TreeParentFinder(DelConfirm_1["DataTransferPath_path"])
            # # 输入的节点是当前节点,返回的是父节点
            # node = parentnode.find_parent(Bus_id)
            tree = json2tree(DelConfirm_1["DataTransferPath_path"])
            node = tree.parent(Bus_id)
            print("本节点"+Bus_id+"父节点为：", node)
            print("recvAckDict的内容是：", recvAckDict)
            if node is not None:
                # node是父节点
                # 寻找到自己节点的父节点，然后就可以发送信息了
                node = node._identifier
                delconfirmstr = {
                    "affairs_id": DelConfirm_1["affairs_id"],
                    "from_bus_id": Bus_id,
                    "to_bus_id": node,
                    "user_id": DelConfirm_1["user_id"],
                    "info_id": DelConfirm_1["info_id"],
                    "DataTransferPath_path": DelConfirm_1["DataTransferPath_path"],
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
                    "DataTransferPath_path": DelConfirm_1["DataTransferPath_path"],
                   # "DelConfirmSignatureDict": {Bus_id: signature}  # string bus_id: string signature的集合
                    "DelConfirmSignatureDict": sign
                }
                # 把签名信息转成十六进制
                hex_string = DelConfirm["DelConfirmSignatureDict"][Bus_id].hex()
                DelConfirm["DelConfirmSignatureDict"][Bus_id] = hex_string
                DelConfirm = json.dumps(DelConfirm)

                # 此处的ip和port应该通过父节点的ID去查找
                ip = "127.0.0.1"
                with open('ID.csv', 'r') as csvfile:
                    port = ""
                    reader = csv.DictReader(csvfile)
                    for row in reader:
                        if row['ID'] == node:
                            port = row['port']
                url = f"http://{ip}:{port}/confirm/postx/endpointx"  # 替换为自己的实际目标URL
                print(url)
                response = requests.post(url, json=DelConfirm)
                # 检查响应
                if response.status_code == 200:
                    print("POST请求成功")
                    print("响应内容:", response.text)
                else:
                    print("POST请求失败")
                    print("响应状态码:", response.status_code)
                recvAckDict.clear()
                return "结束"
            else:#表示自己是源节点的，没有父节点
                # 给用户删除通知确认反馈
                print("验证结束")
                recvAckDict.clear()
                return "结束"

if __name__ == "__main__":
    # userroute.run(host='127.0.0.1', port=int(sys.argv[2]), debug=True)
    userroute.run(host='127.0.0.1', port= 20001, debug=True)