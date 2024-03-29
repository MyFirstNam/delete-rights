from flask import Flask, request, jsonify, Blueprint
from ConnectSysDel import ConnectSysDel
from DelTrigger import DelTrigger
import pprint
import requests
import json
import hashlib
import csv
import time
import DelNotifyOther, SignAndKey
from InfoMemory import InfoMemory
from Json2Tree import json2tree
from ConnectOne import ConnectOne
from Path2Json import gen_tree_json
import threading

# todo 每次启动路由，标识当前路由（企业）ID，通过外部标识输入参数
Bus_id = "b1000"

# 处理删除意图or删除通知的的路由及其视图函数
userroute = Flask(__name__)
@userroute.route("/test/post/endpoint", methods=['POST'])
# POST格式为JSON格式
def intentionAly():
    # 通过判断post是否包含time、count字段，来调用DelTrigger中不同的函数
    # todo 返回一个bool值表示直接的后继节点是否受到删除通知
    data = request.json
    data = json.loads(data)
    # 三种情况，普通请求，带有时间请求，带有次数次数请求
    # todo 把下面的判断整合到类里面
    trigger = DelTrigger()
    if "time_limit" in data and "count_limit" not in data:
        deleteReq = trigger.timeTrigger(data)  # 函数返回值删除请求，为一个dict
        Timememory = data["time_limit"]
        Countmemory = 0
        triggerType = "计时触发"
    elif "time_limit" not in data and "count_limit" in data:
        deleteReq = trigger.countTrigger(data)
        Timememory = ""
        Countmemory = data["count_limit"]
        triggerType = "计次触发"
    else:
        deleteReq = trigger.deleteTrigger(data)
        Timememory = ""
        Countmemory = 0
        triggerType = "按需触发"
    # 获取到删除请求（已经从删除意图解析成为了删除请求）

    # 向中心监管机构请求删除流转路径
    with open('ID.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['ID'] == "b1099":  # 默认中心监管机构的ID是b1099
                port = row['port']
    ip = '127.0.0.1'  # 课题一开放的ip
    connectone = ConnectOne(ip, port)
    dataTransferPath = connectone.reqPah(deleteReq["affairs_id"], deleteReq["info_id"])
    dataTransferPath = json.loads(dataTransferPath)
    # dataTransferPath = [
    #       {"from": "b1000", "to": "b1001"},
    #       {"from": "b1000", "to": "b1003"},
    #       {"from": "b1001", "to": "b1002"},
    #       {"from": "b1003", "to": "b1004"}
    # ]
    pprint.pprint(dataTransferPath)


    deleteNotifyTree = gen_tree_json(dataTransferPath, Bus_id)
    tree = json2tree(deleteNotifyTree)
    print(tree)
    # 删除通知生成与分发
    # (1) 首先生成删除通知
    # (2) 当前节点，通过deleteNotifyTree,得到后继节点，即后面应该发给那些节点（如果当前节点直接就是叶子节点，则不需要转发，直接返回一个true）

    nextNode = [i._identifier for i in tree.children(Bus_id)]  # 负责根据当前节点，寻找下一个节点（子节点的所有唯一标识符id），返回一个list

    # (1-1)生成删除通知，将deleteReq与deleteNotifyTree结合一下
    delNotice = {
        "affairs_id": deleteReq["affairs_id"],
        "user_id": deleteReq["user_id"],
        "info_id": deleteReq["info_id"],
        "from_bus_id": Bus_id,
        "to_bus_id": "",  # 实现过程中，此参数应该是一个字符串，表示后续发送给某一个节点，在生成删除通知时需要根据情况更新
        "deleteMethod": deleteReq["deleteMethod"],
        "deleteGranularity": deleteReq["deleteGranularity"],
        "deleteNotifyTree": deleteNotifyTree  # 一个JSON
    }

    # （1-2）根据删除通知生成删除指令,并且发送给确定性删除系统
    ip = "202.243.25.166"  # todo 模拟域0中确定性删除系统的ip和port,通过查询来获取
    port = 9650  # tips:对于删除通知与确认系统测试，可以用同一个ip,同一个端口来模拟确定性删除系统
    start = time.time()
    for i in range(10000):
        connectSysdel = ConnectSysDel(ip, port)   # 传入确定性删除系统的IP和port
        delInstruction = connectSysdel.buildDelIns(delNotice)
    end = time.time()
    print("删除指令生成时间为: %s ms"%((end-start)*1000))
    response = connectSysdel.sendDelIns(delInstruction)
    print(response)

    # 存储目前已经获取的信息  # todo 换数据库修改此处
    # processor = InfoMemory(host="localhost", user="root", port=3306, password="123456", database="project26")
    # processor = InfoMemory(host="10.170.42.45", port=3306, user="myuser", password="mypassword", database="project26")
    # processor.insert_record(delNotice["user_id"], delNotice["info_id"],delNotice["deleteMethod"],delNotice["deleteGranularity"],delNotice["deleteNotifyTree"],triggerType,Bus_id,Timememory,Countmemory)
    # 如果后继节点不为空
    if nextNode != None:
        DelNotifyOther.CountSend(nextNode, delNotice).runtest()

    # 发送：delNotice    接收：删除通知应答 DelNoticeResponse
    # 将所有返回的DelNoticeResponse组成一个list,对其中的isReceive进行判断，返回一个时候后继节点是否全部接收的bool

    # 后继节点为空
    else:
        return True
    return f"企业节点{Bus_id}接收请求信息成功！"



recvAckDict = {
}

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
            # sign = {}
            # for item in recvAckDict[DelConfirm_1["affairs_id"]][1:]:
            #     sign.update(item)
            # receive = len(sign)
            # print(receive)
            # num = tree.__len__() - 1
            # print("删除通知成功率：", receive / num)

            print("收到第一个子节点确认，但是还不够！")
            print("recvAckDict的内容是：", recvAckDict)
            # sign = {}
            # for item in recvAckDict[DelConfirm_1["affairs_id"]][1:]:
            #     sign.update(item)
            # receive = len(sign)
            # print(receive)
            # num = tree.__len__() - 1
            # print("删除通知成功率：", receive / num)
            return "确认数不等于子节点数！"
        else:
            # todo 这需要把recvAckDict对应项删除
            # 生成自己的签名
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
                # port = 20006
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
                print("验证全部结束！")
                # 计算删除成功率
                sign = {}
                for item in recvAckDict[DelConfirm_1["affairs_id"]][1:]:
                    sign.update(item)
                receive = len(sign)
                print(receive)
                num = tree.__len__()-1
                print("删除通知成功率：", receive/num)
                # 此时开始在数据库中存储存证信息
                sign = {
                }
                for item in recvAckDict[DelConfirm_1["affairs_id"]][1:]:
                    sign.update(item)
                sign = json.dumps(sign)
                # todo 换数据库修改此处
                # processor = InfoMemory(host="localhost", user="root", port=3306, password="123456",database="project26")
                # processor = InfoMemory(host="10.170.42.45", port=3306, user="myuser", password="mypassword", database="project26")
                # processor.insert_newrecord(DelConfirm_1["user_id"],sign,DelConfirm_1["info_id"])
                recvAckDict.clear()
                return "结束"




if __name__ == "__main__":
    # userroute.register_blueprint(route)
    # userroute.register_blueprint(confirm)
    userroute.run(host='127.0.0.1', port=20000, debug=True)
    # userroute.run(host='127.0.0.1', port=int(sys.argv[2]), debug=True)
    # userroute.run(host='127.0.0.1', port= 20001, debug=True)