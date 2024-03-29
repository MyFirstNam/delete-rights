"""
监听来自企业的消息，与真实的中心监管机构交互
此py文件中，包含个路由：
1.监听来自企业节点发送的数据流转路径请求：
    接收内容：数据流转请求
    返回内容：删除通知（删除通知树，时间戳，IBBE（信息载荷））+ 明文树(为了配合!)
    1-1(附加功能) 开启一个新的路由
      监听来自企业节点发送的删除通知确认信息，进行验证
      理论上，验证一定会通过的，实际上，也会通过的
      如果不通过，就该溯源了！！！！！！！！

2.监听来自企业节点发送的日志内容:
    接收内容：日志信息

3.监听来自企业节点发送的异常信息内容：
    接收内容：异常信息
"""

# 导入文件中需要的包和相关文件
from flask import Blueprint, request, Flask, jsonify
from threading import Thread
from time import sleep
from NodeSimulation.Model.EnterpriseNode import EnterpriseNode
from CenterSimulation.Utils.pathParamCreate import path_request_create
from CenterSimulation.Utils.converrtPathformat import gen_tree_json
from CenterSimulation.Utils.Json2Tree import json2tree
from CenterSimulation.Model.PathReqAndEncryption import PathReqAndEncryption
from CenterSimulation.Model.SecurityProtocol import MessageDecoder
from CenterSimulation.Model.SecurityProtocol.protocol_utils.busid_to_secret import busid_to_IBBE_secret
from CenterSimulation.Utils.IBBEKeyRead import IBBEKeyRead
from CenterSimulation.Utils.delNotifyAckVerify import delNotifyAckVerify
import requests
import json
import logging
import datetime
import copy
import pickle
from json import dumps
from pypbc import *
from treelib import Tree, Node

center_blue = Blueprint('center', __name__, url_prefix='/center')
# url_prefix 是一个可选参数，它为这个蓝图下的所有路由设置一个公共的URL前缀


# 设置全局变量,临时存储删除确认树，用于后续验证
delNotifytree = {}
# delNotifytree = {
#    "affairs_id: tree 一个Tree对象
# }


# 在定义蓝图之后，发送路由的样例格式如下：
# 127.0.0.1:8080/center/recv_path
@center_blue.route("/receive_path", methods=['POST'])
def recv_path():
    """
    函数说明：
    处理来自企业发送的数据流转信息请求
    具体流程：
        1.解析数据包，向“真实”的中心监管请求数据流转
        2.数据流转路径格式化
        3.数据流转路径加密
        4.信息载荷payload加密
    :return:
    视图函数处理当前流程后，必须有返回值，具体类型多样
        此返回值是返回给发送端
    返回值具体内容：
        1.删除通知（删除通知树+时间戳+IBBE加密的payload）
        2.数据流转树（Tree对象，为了配后后续系统执行）

    接收到的data数据格式样例：
        {
        "affairs_id": "00001",
        "user_id": "u00001",
        "info_id": "a1b2c3d4e5",
        "deleteMethod": "硬件删除",
        "deleteGranularity": "硬件删除"
        "from_bus_id":"b1000"  为了弥补我们系统demo无法根据ip地址查找区分父节点的缺陷
        }
    """

    # 日志打印信息设置
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    data = request.json

    # case1: 正常情况：接收内容为数据流转请求
    try:
        data = json.loads(data)

        # 进一步处理 json_data.生成规范的信息流转路请求
        # 根据删除请求，向中心监管机构请求数据流转记录（返回的其实是删除通知+数据流转树（数据流转记录格式化后的Tree对象））
        # 在我们的设计中，是向代理中心监管机构CenterSimulation请求
        pathReq = PathReqAndEncryption()
        dataTransferPath = pathReq.path_request(data["info_id"], data["affairs_id"])

        # 格式转换
        pathformat = gen_tree_json(dataTransferPath, data["from_bus_id"])
        # print(pathformat)
        # print(type(pathformat))
        deleteNotifyTree = json2tree(pathformat)
        logging.info("经过对获取的数据流转路径进行格式化转换，转换结果如下:")
        print(deleteNotifyTree)
        # 深度拷贝一下这个树，不然加密的时候会增加空叶子
        deleteNotifyTreecopy = copy.deepcopy(deleteNotifyTree)

        # 获取当前时间，生成时间戳
        current_time = datetime.datetime.now()
        timestamp = current_time.strftime("%Y-%m-%d%H:%M:%S")
        # timestamp = "12345678"

        # 开始对数据流转树进行加密，生成删除通知树，同时将删除确认树存储起来用于验证
        NotifyTreeEncry, ConfirmTree = pathReq.pathEncryprtion(deleteNotifyTree, data, timestamp)

        # 用全局变量进行一下删除确认树临时存储，用于后续验证
        global delNotifytree
        if data["affairs_id"] not in delNotifytree:
            # （1）查询不到，插入一项affairs_id,保存next_segment_tree_list
            delNotifytree[data["affairs_id"]] = ConfirmTree
        else:
            # (2) 查询到了
            pass

        # 信息载荷IBBE加密
        # 当初为了方便查询父节点，对于中心监管机构，为了生成树，加入了”from_bus_id“字段，在payload加密时，去掉此字段，
        data.pop('from_bus_id', 'Not Found')
        payloadEnc = pathReq.payloadEncryption(deleteNotifyTreecopy, data)

        ###############################################################
        # 解密测试
        # params, MSK, PK = IBBEKeyRead()
        # params = Parameters(params.__str__())
        #
        # ID = 'b1000'
        # pairing1 = Pairing(params)
        # SK = Element(pairing1, G2, busid_to_IBBE_secret(ID))
        # S = ['b1000', 'b1001', 'b1002', 'b1003', 'b1004']
        # payload = json.loads(payloadEnc)
        # # payload = payloadEnc
        # Hdry = payload[0]
        # for i, (Hdr, y) in enumerate(Hdry):
        #     Hdr[0] = Element(pairing1, G1, Hdr[0])
        #     Hdr[1] = Element(pairing1, G2, Hdr[1])
        #     Hdry[i] = (Hdr, y)
        #
        # payload_list = list(payload)
        # payload_list[0] = Hdry
        # payload = tuple(payload_list)
        # pub_param = (S, SK, ID, PK)
        #
        # decoder = MessageDecoder.Decoder()
        # decoder.setParams(params.__str__())
        # newPlaintext = ""
        # try:
        #     newPlaintext = decoder.ibbeDecode(pub_param, payload)
        # except Exception as e:
        #     print(e)
        # print(newPlaintext)
        #
        # # 下面这两行其实没有也行
        # newPlaintext = json.loads(newPlaintext)
        # plaintext = dumps(newPlaintext)
        #
        # decoder = MessageDecoder.Decoder()
        # data.pop('from_bus_id', 'Not Found')
        #
        # next_bus_ip_list, next_segment_tree_list = decoder.treeDecode('center', 'b1000', timestamp, plaintext,
        #                                                               NotifyTreeEncry)
        # print(next_bus_ip_list)
        # print(next_segment_tree_list)
        # def aaa(from_bus_id, to_bus_id, time_stamp, plaintext, segment_tree):
        #     print(from_bus_id + "--->" + to_bus_id)
        #     next_bus_ip_list, next_segment_tree_list = decoder.treeDecode(from_bus_id, to_bus_id, time_stamp,plaintext, segment_tree)
        #     for i, j in zip(next_bus_ip_list, next_segment_tree_list):
        #         if i == "center":
        #             break
        #         else:
        #             aaa(to_bus_id, i, time_stamp, plaintext, j)
        #
        # aaa('center', 'b1000', timestamp, plaintext, NotifyTreeEncry)

        # 将Tree对象序列化
        # 删除通知树序列化
        # NotifyTreeEncry = NotifyTreeEncry.to_dict(with_data=True)
        # NotifyTreeEncry = json.dumps(NotifyTreeEncry, indent=4)
        # print(type(NotifyTreeEncry))

        # !!!!!!!一定要把reverse参数设置为True，不然反序列化出来以后有编码问题
        # 虽然现在偶尔也会有编码问题，但是概率很小
        NotifyTreeEncry = NotifyTreeEncry.to_json(sort=False)

        # 明文树序列化
        # deleteNotifyTreecopy = deleteNotifyTreecopy.to_dict(with_data=True)
        # deleteNotifyTreecopy = json.dumps(deleteNotifyTreecopy, indent=4)
        # print(type(deleteNotifyTreecopy))
        deleteNotifyTreecopy = deleteNotifyTreecopy.to_json(sort=False)

        # 编码错误测试

        # data_dict = json.loads(NotifyTreeEncry)
        # print(data_dict)
        # print(type(data_dict))
        #
        # def build_tree_from_dict(data, tree=None, parent=None):
        #     if tree is None:
        #         tree = Tree()
        #         # 假定根节点已经在字典的键中指定了，我们用'data'来创建根节点
        #         tree.create_node(identifier='root', data=data.get('data'))
        #         # 递归添加子节点
        #         build_tree_from_dict(data, tree, 'root')
        #     else:
        #         if isinstance(data, dict):
        #             for key, value in data.items():
        #                 if key == 'children':
        #                     for child in value:
        #                         for child_key, child_value in child.items():
        #                             tree.create_node(identifier=child_key, parent=parent)
        #                             build_tree_from_dict(child_value, tree, child_key)
        #                 else:
        #                     tree.create_node(identifier=key, parent=parent)
        #                     if 'children' in value:
        #                         build_tree_from_dict(value['children'], tree, key)
        #     return tree
        #
        # tree = build_tree_from_dict(data_dict['root'])
        #
        # NotifyTreeEncry = tree

        # params, MSK, PK = IBBEKeyRead()
        # params = Parameters(params.__str__())
        # decoder = MessageDecoder.Decoder()
        # decoder.setParams(params.__str__())
        # plain = {'affairs_id': '00001', 'user_id': 'u00001', 'info_id': 'a1b2c3d4e5', 'deleteMethod': 'yingjianshanchu',
        #          'deleteGranularity': 'age'}
        # plaintext = json.dumps(plain)
        #
        # # plaintext = newPlaintext
        #
        # def aaa(from_bus_id, to_bus_id, time_stamp, plaintext, segment_tree):
        #     print(from_bus_id + "--->" + to_bus_id)
        #     next_bus_ip_list, next_segment_tree_list = decoder.treeDecode(from_bus_id, to_bus_id, time_stamp, plaintext,
        #                                                                   segment_tree)
        #     print(next_bus_ip_list)
        #     print(next_segment_tree_list[0])
        #     # for i, j in zip(next_bus_ip_list, next_segment_tree_list):
        #     #     if i == "center":
        #     #         break
        #     #     else:
        #     #         aaa(to_bus_id, i, time_stamp, plaintext, j)
        #
        # time = timestamp
        # tree = json2tree(NotifyTreeEncry)
        # # tree = NotifyTreeEncry
        # print(tree)
        # aaa('center', 'b1000', time, plaintext, tree)

        # 重组删除通知内容
        deleteNotifyInfo = (NotifyTreeEncry, timestamp, payloadEnc, deleteNotifyTreecopy)

        return jsonify(deleteNotifyInfo), 200

    # case2: 异常情况：解析的字符串不是有效的JSON格式
    except json.JSONDecodeError:
        return '中心监管机构接收内容为无效的JSON！', 400


@center_blue.route("/receive_confirm", methods=['POST'])
def recv_confirm():
    """
    函数说明：
    验证来自企业发送的删除通知签名信息
    具体流程：
        1.将签名信息与已经生成的删除确认树进行字符串对比
    :return:
    视图函数处理当前流程后，必须有返回值，具体类型多样
        此返回值是返回给发送端
    返回值具体内容：
        1.验证结果
    """
    data = request.json

    # case1: 正常情况：接收内容为删除通知确认信息
    try:
        data = json.loads(data)
        logging.info("代理中心监管机构接收到的删除通知确认信息如下:")
        print(data)
        logging.info("临时存储的删除通知确认树如下:")
        print(delNotifytree[data["affairs_id"]])
        # 开始进行删除通知结果验证

        node_set = set(delNotifyAckVerify(delNotifytree[data["affairs_id"]])[0])
        print(node_set)
        # print(type(node_set))

        # 开始验证

        # 用于存储结果的字典，键是原字典的键，值是一个布尔值列表，指示每个元素是否在result列表中
        presence_in_result = {}

        # 遍历字典
        for key, value_list in data['DelConfirmSignatureDict'].items():
            # 检查每个元素是否在result列表中，并存储结果
            presence_in_result[key] = [value in node_set for value in value_list]

        # 打印验证结果
        logging.info("验证结果如下：")
        for key, presence_list in presence_in_result.items():
            print(f"{key}: {presence_list}")

        # 清空affairs_id对应的公共变量
        if data["affairs_id"] in delNotifytree:
            del delNotifytree[data["affairs_id"]]

        return '中心监管已成功接收到删除通知确认信息的JSON格式数据！', 200

    # case2: 异常情况：解析的字符串不是有效的JSON格式
    except json.JSONDecodeError:
        return '代理中心机构接收内容为无效的JSON！', 400


@center_blue.route("/receive_logging", methods=['POST'])
def recv_logging():
    """
    函数说明：
    1.作为代理proxy,转发删除通知的“日志”信息

    具体方式：
    :return:
    视图函数处理当前流程后，必须有返回值，具体类型多样
        此返回值是返回给发送端
    """
    data = request.json

    # case1: 正常情况：接收内容为删除通知的日志信息
    try:
        data = json.loads(data)

        print(data)

        return "", 200
    # case2: 异常情况：解析的字符串不是有效的JSON格式
    except json.JSONDecodeError:
        return '代理中心机构接收内容为无效的JSON！', 400


@center_blue.route("/receive_exception", methods=['POST'])
def recv_exception():
    """
    函数说明：
    1.作为代理proxy,转发删除通知的“异常”信息，给真实的中心监管机构
    :return:
    试图函数处理当前流程后，必须有返回值，具体类型多样
        此返回值是返回给发送端
    """
    data = request.json

    # case1: 正常情况：接收内容为异常信息
    try:
        data = json.loads(data)
        logging.info("代理中心机构已经成功接收到异常信息（删除通知发送异常/删除通知确认回传异常）！")
        print(data)

        return "代理中心机构成功接收到异常信息内容", 200
    # case2: 异常情况：解析的字符串不是有效的JSON格式
    except json.JSONDecodeError:
        return '代理中心机构内容为无效的JSON！', 400


appb = Flask(__name__)
appb.register_blueprint(center_blue)

if __name__ == "__main__":
    appb.run(host='127.0.0.1', port=20100, debug=True)
