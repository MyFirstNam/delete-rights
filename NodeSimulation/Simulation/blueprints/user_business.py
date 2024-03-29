import sys

sys.path.append('/home/dengx/deng_delete2_6/')

"""
监听来自用户或者其他企业的消息
此py文件中，包含三个路由：
1.监听来自用户/上级节点发送的内容：
    1.删除意图（用户）
2.监听来自上级节点发送的内容:
    1.删除通知（上级节点）
3.监听来自下级节点发送的内容：
    1.删除通知确认
"""

# 导入文件中需要的包和相关文件
from flask import Blueprint, request, Flask
from threading import Thread
from time import sleep
from NodeSimulation.Model.EnterpriseNode import EnterpriseNode
from NodeSimulation.Utils.delNotifyAckBack import delNotifyAckBack
import requests
import json
import logging
from NodeSimulation.Utils.NotifyInfoDecryption import NotifyInfoDec
import threading

# 将被app.py引用的变量
enterprise_blue = Blueprint('enterprise', __name__, url_prefix='/enterprise')
# url_prefix 是一个可选参数，它为这个蓝图下的所有路由设置一个公共的URL前缀


# 设置全局变量,节点（企业）ID
# todo 将来代码与数据分离
# bus_id = "b1000"
bus_id = sys.argv[1]

# 定义四个公共变量
# 一个用来存储自己的父节点(用于删除通知确认信息回传)
# 一个用来临时存储自己修改过的删除通知树
# 一个用来临时存储自己接收到子节点的删除通知确认消息
# 一个用来临时存储自己接收经过解密的明文信息
CurrentIDparent = {}
CurrentPlaintext = {}
CurrentNotifytree = {}
acceptedAckInfo = {}
# 格式样例
# CurrentIDparent = {"affairs_id":"b1000"}
# CurrentPlaintext = {"affairs_id":{"userID":"000101"}}
# CurrentNotifytree = {"affairs_id":["asdffdsf","dsasadsads]}
# acceptedAckInfo = {
#     "affairs_id": [2, {"bx1000": "0xasdas"}, {"bx1001": "0xasdfas"}]
# }


# 在定义蓝图之后，发送路由的样例格式如下：
# 127.0.0.1:8080/enterprise/recv_from_user
@enterprise_blue.route("/receive_user", methods=['POST'])
def recv_user():
    """
    函数说明：
    处理来自用户发送的删除意图
    具体流程：
        1.解析删除意图，判断删除触发方式（计时/计次/按需）
            计次/按需 返回删除请求delrequest, 计时无返回值

    :return:
    视图函数处理当前流程后，必须有返回值，具体类型多样
        此返回值是返回给发送端
    """
    data = request.json

    # case1: 正常情况：接收内容为删除意图
    try:
        data = json.loads(data)

        # 进一步处理 json_data

        def background_task():
            # 这里执行耗费时间处理删除意图的操作
            # 判断触发类型
            # 生成删除请求
            enterprise = EnterpriseNode(bus_id)
            delrequest = enterprise.del_intention_parsing(data)
            if delrequest is None:
                return
            elif delrequest is False:
                return
            else:
                logging.info("按需触发，计次触发正在处理·····")
                logging.info("删除请求(delrequest)如下:")
                logging.info(delrequest)

            # 根据删除请求，向中心监管机构请求数据流转记录（返回的其实是删除通知+数据流转树（数据流转记录格式化后的Tree对象））
            # 在我们的设计中，是向代理中心监管机构CenterSimulation请求

            # 调用删除通知范围确定与删除通知生成模块
            ciphertext = enterprise.del_Notify_scopeAndgenerate(delrequest)
            ciphertext = json.loads(ciphertext)

            # 调用解密函数
            # 这个参数将来需要看如何改改，这里是一个程序中写死的定值，是因为加解密中写死了
            busid_parent = 'center'

            # 获取下一个节点列表,修改后的删除通知树[列表]，明文[字典]，删除通知密文[列表], 明文树[Tree]
            next_bus_id_list, next_segment_tree_list, plaintext, EncInfolist, tree_plaintext = NotifyInfoDec(bus_id,
                                                                                                        busid_parent,
                                                                                                             ciphertext)
            # 存储一下，用于后续删除通知确认信息生成与回传
            # 定义全局变量是最差的做法，但是目前没什么好的方法
            global CurrentIDparent
            global CurrentNotifytree

            if plaintext["affairs_id"] not in CurrentIDparent:
                # （1）查询不到，插入一项affairs_id,保存busid_parent
                CurrentIDparent[plaintext["affairs_id"]] = busid_parent
            else:
                # (2) 查询到了
                pass

            if plaintext["affairs_id"] not in CurrentNotifytree:
                # （1）查询不到，插入一项affairs_id,保存next_segment_tree_list
                CurrentNotifytree[plaintext["affairs_id"]] = next_segment_tree_list
            else:
                # (2) 查询到了
                pass

            if plaintext["affairs_id"] not in CurrentPlaintext:
                # （1）查询不到，插入一项affairs_id,保存next_segment_tree_list
                CurrentPlaintext[plaintext["affairs_id"]] = plaintext
            else:
                # (2) 查询到了
                pass

            # 先给自己企业的确定性删除系统进行删除指令生成分解与分发
            enterprise.del_instruction_decAnddis(plaintext, tree_plaintext)

            # 给后续企业发送删除通知
            enterprise.del_Notify_generateAndsend(next_bus_id_list, next_segment_tree_list, EncInfolist, bus_id,
                                                  plaintext, tree_plaintext, busid_parent)

        # 重新开一个线程的原因是因为为了给发送者及时返回信息，不需要等待数据请求删除处理的时间
        thread = Thread(target=background_task)
        thread.start()

        return '企业节点已成功接收到删除意图请求的JSON格式数据！', 200

    # case2: 异常情况：解析的字符串不是有效的JSON格式
    except json.JSONDecodeError:
        return '节点接收内容为无效的JSON！', 400


@enterprise_blue.route("/receive_enter", methods=['POST'])
def recv_enter():
    """
    函数说明：
    1.处理来自上级节点（企业）的删除通知
      功能一：解密接收到的内容
      功能二：给自己的确定性删除系统发送删除指令
      功能三：生成新的删除通知，给后续企业发送删除通知
      功能四：日志存证

    具体方式：根据接收内容判断具体执行操作
    :return:
    视图函数处理当前流程后，必须有返回值，具体类型多样
        此返回值是返回给发送端
    """
    data = request.json

    # case1: 正常情况：接收内容为删除通知
    try:
        data = json.loads(data)

        # 进一步处理 json_data
        def background_task():
            logging.info("企业接收到的内容(删除通知)如下:")
            print(data)
            print(type(data))
            # print(data[0])
            # print(type(data[0]))
            # print(data[1])
            # print(type(data[1]))
            # print(data[2])
            # print(type(data[2]))
            # print(data[3])
            # print(type(data[3]))
            # print(data[4])
            # print(type(data[4]))

            enterprise = EnterpriseNode(bus_id)

            # 首先从接收到的内容中分解出父节点ID
            # 本质上应该是根据发送端的IP地址获取，但是demo使用同一IP，所以多加了一个参数
            busid_parent = data[4]

            # 调用解密函数
            # 获取下一个节点列表,修改后的删除通知树[列表]，明文[字典]，删除通知密文[列表], 明文树[Tree]
            next_bus_id_list, next_segment_tree_list, plaintext, EncInfolist, tree_plaintext = NotifyInfoDec(bus_id,
                                                                                                             busid_parent,
                                                                                                             data)
            # 存储一下，用于后续删除通知确认信息生成与回传
            # 定义全局变量是最差的做法，但是目前没什么好的方法
            global CurrentIDparent
            global CurrentNotifytree

            if plaintext["affairs_id"] not in CurrentIDparent:
                # （1）查询不到，插入一项affairs_id,保存busid_parent
                CurrentIDparent[plaintext["affairs_id"]] = busid_parent
            else:
                # (2) 查询到了
                pass

            if plaintext["affairs_id"] not in CurrentNotifytree:
                # （1）查询不到，插入一项affairs_id,保存next_segment_tree_list
                CurrentNotifytree[plaintext["affairs_id"]] = next_segment_tree_list
            else:
                # (2) 查询到了
                pass

            if plaintext["affairs_id"] not in CurrentPlaintext:
                # （1）查询不到，插入一项affairs_id,保存next_segment_tree_list
                CurrentPlaintext[plaintext["affairs_id"]] = plaintext
            else:
                # (2) 查询到了
                pass

            print(next_bus_id_list)
            print(type(next_bus_id_list))
            print(next_segment_tree_list)
            print(type(next_segment_tree_list))
            print(plaintext)
            print(type(plaintext))
            print(EncInfolist)
            print(type(EncInfolist))
            print(tree_plaintext)
            print(type(tree_plaintext))

            # 先给自己企业的确定性删除系统进行删除指令生成分解与分发
            enterprise.del_instruction_decAnddis(plaintext, tree_plaintext)

            # 给后续企业发送删除通知
            # 如果后续企业为空，也会回溯删除通知确认
            enterprise.del_Notify_generateAndsend(next_bus_id_list, next_segment_tree_list, EncInfolist, bus_id,
                                                  plaintext, tree_plaintext, busid_parent)

        thread = Thread(target=background_task)
        thread.start()
        return '对方节点已成功接收到删除通知的JSON格式数据！', 200

    # case2: 异常情况：解析的字符串不是有效的JSON格式
    except json.JSONDecodeError:
        return '对方节点接收内容为无效的JSON！', 400


# 定义一个线程锁，保证公共变量一次只能被一次修改
recvAckDictLock = threading.Lock()


@enterprise_blue.route("/receive_enter_confirm", methods=['POST'])
def recv_enter_confirm():
    """
    函数说明：
    处理来自下级节点（企业）的删除通知确认
    具体方式：接收下级的删除通知确认，生成自己删除通知确认，一并回送给上级节点
                如果没有上级节点，给用户反馈，同时执行其他操作
    :return:
    试图函数处理当前流程后，必须有返回值，具体类型多样
        此返回值是返回给发送端
    """

    data = request.json

    # case1: 正常情况：接收内容为子节点的删除通知确认
    try:
        data = json.loads(data)
        logging.info("接收到的单个子节点删除通知确认信息如下：")
        print(data)

        # 通过删除通知确认中的删除流转路径查询自己有几个子节点，之后通过根据affairs_id查看recvAckDict全局变量是否达到子节点个数
        with recvAckDictLock:
            if data["affairs_id"] not in acceptedAckInfo:
                # （1）查询不到，插入一项affairs_id;1,同时只需要保留签名即可
                acceptedAckInfo[data["affairs_id"]] = [1, data["DelConfirmSignatureDict"]]
            else:
                # (2) 查询到了，则将affairs_id对应的值加1
                acceptedAckInfo[data["affairs_id"]][0] = acceptedAckInfo[data["affairs_id"]][0] + 1
                acceptedAckInfo[data["affairs_id"]].append(data["DelConfirmSignatureDict"])

            # 先根据修改的删除通知树中的Tree个数，判断有几个子节点
            childrencount = len(CurrentNotifytree[data["affairs_id"]])

            # 没收全删除通知确认消息
            if childrencount != acceptedAckInfo[data["affairs_id"]][0]:
                logging.info(
                    f"本企业{bus_id}对于本条信息的'子节点企业'个数为{childrencount},已经收到的删除通知确认个数为{acceptedAckInfo[data['affairs_id']][0]}, 二者不相等，继续等待···")

                return "父节点已经成功接收到删除通知确认信息", 200

            # 收全删除通知确认消息
            else:
                logging.info(
                    f"本企业{bus_id}对于本条信息的'子节点企业'个数为{childrencount},已经收到的删除通知确认个数为{acceptedAckInfo[data['affairs_id']][0]},二者相等，继续执行后续操作")

                # 生成自己的签名，同时组合接收到的删除通知确认消息
                dict_ack = {
                    bus_id: []
                }
                DelConfirm = {
                    "DelConfirmSignatureDict": {}
                }

                for item in acceptedAckInfo[data["affairs_id"]][1:]:
                    DelConfirm["DelConfirmSignatureDict"].update(item)

                for tree in CurrentNotifytree[data["affairs_id"]]:
                    dict_ack[bus_id].append(tree.root)

                DelConfirm["affairs_id"] = data["affairs_id"]
                DelConfirm["DelConfirmSignatureDict"].update(dict_ack)
                logging.info("删除通知确认内容为:")
                print(DelConfirm)

                # 开始判断父亲是否为center
                # 父节点为center，向代理中心监管机构回传确认信息
                if CurrentIDparent[data["affairs_id"]] == 'center':
                    logging.info("判断父节点为‘center’，回传删除通知确认信息")

                    # 在这里向代理中心监管机构回传删除通知确认信息进行验证
                    delNotifyAckBack(CurrentIDparent[data["affairs_id"]], DelConfirm,
                                     CurrentPlaintext[data["affairs_id"]], bus_id)

                    # 清空affairs_id对应的公共变量
                    if data["affairs_id"] in acceptedAckInfo and data["affairs_id"] in CurrentIDparent and data["affairs_id"] in CurrentNotifytree and data["affairs_id"] in CurrentPlaintext:
                        del acceptedAckInfo[data["affairs_id"]]
                        del CurrentNotifytree[data["affairs_id"]]
                        del CurrentIDparent[data["affairs_id"]]
                        del CurrentPlaintext[data["affairs_id"]]

                    return "父节点已经成功接收到删除通知确认信息", 200
                # 父节点不为center，则回传删除通知确认信息
                else:
                    logging.info(f"判断父节点为{CurrentIDparent}，回传删除通知确认信息")
                    delNotifyAckBack(CurrentIDparent[data["affairs_id"]], DelConfirm, CurrentPlaintext[data["affairs_id"]], bus_id)

                    # 清空affairs_id对应的公共变量
                    if data["affairs_id"] in acceptedAckInfo and data["affairs_id"] in CurrentIDparent and data["affairs_id"] in CurrentNotifytree and data["affairs_id"] in CurrentPlaintext:
                        del acceptedAckInfo[data["affairs_id"]]
                        del CurrentNotifytree[data["affairs_id"]]
                        del CurrentIDparent[data["affairs_id"]]
                        del CurrentPlaintext[data["affairs_id"]]

                    return "父节点已经成功接收到删除通知确认信息", 200

    # case2: 异常情况：解析的字符串不是有效的JSON格式
    except json.JSONDecodeError:
        return '父节点接收到删除通知确认信息格式错误，不符合格式要求！', 400


app = Flask(__name__)
app.register_blueprint(enterprise_blue)

if __name__ == "__main__":
    # app.run(host='127.0.0.1', port=20000, debug=True)
    app.run(host='127.0.0.1', port=int(sys.argv[2]), debug=True)
