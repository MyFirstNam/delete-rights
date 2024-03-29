"""
此py文件定义"代理"中心机构事务处理类：
类中包含的函数的具体功能：
    1.向“真实”的中心监管请求数据流转
    2.数据流转路径加密
    3.信息载荷payload加密
"""

import logging
import requests
import json
import os
import time
import configparser
import datetime
import socket
from json import dumps
from pypbc import *
from CenterSimulation.Model.SecurityProtocol import MessageEncoder
from CenterSimulation.Model.SecurityProtocol import MessageDecoder
from CenterSimulation.Utils.pathParamCreate import path_request_create
from CenterSimulation.Utils.IBBEKeyRead import IBBEKeyRead, collect_node_values
from CenterSimulation.Model.SecurityProtocol.protocol_utils.busid_to_secret import busid_to_IBBE_secret


class PathReqAndEncryption:

    # 日志打印信息设置
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def __init__(self):
        pass

    def path_request(self, globalID, affairsID):
        """
        函数功能说明：
        向”真实“的中心监管机构请求数据流转路径，request的一个过程

        :param affairsID: 事务ID，与globalID(infoID)组成evidenceID
        :param globalID: 其实就是infoID，课题内部称为infoID，与课题一交互称为为globalID
        :return: 路由访问返回课题一返回的全部内容

        课题一返回的格式样例(仅展示data字段)：
        "data": {
            "infoID": "283749abaa234cde",
            "dataTransferPath": [
                { "from": "b1000", "to": "b1001" },
                { "from": "b1001", "to": "b1002" },
                { "from": "b1002", "to": "b1003" }
                ]
            }
        """
        # 请求数据格式规范
        pathreq = path_request_create(globalID, affairsID)
        logging.info(f'向中心监管机构请求info为{globalID}的信息流转记录，此次事务的id为{affairsID}')
        reqTree = json.dumps(pathreq)

        # 请求路由获取
        # 获取当前文件的绝对路径
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # 设置相对于当前文件的路径
        config_folder = os.path.join(current_dir, '..', 'Resource')
        config_file = 'ipAndPort.txt'

        # 组合并规范化路径
        config_path = os.path.normpath(os.path.join(config_folder, config_file))
        with open(config_path, "r") as f:
            url = f.read()

        max_retries = 3  # 最大重试次数
        for attempt in range(max_retries):
            response = requests.post(url, json=reqTree)
            if response.status_code == 200:
                logging.info("向中心监管机构发起数据流转路径的POST请求成功！")
                return json.loads(response.text)
            else:
                logging.error(f"尝试 #{attempt + 1}: 向中心监管机构发起数据流转路径的POST请求失败！")
                logging.error("响应状态码: " + str(response.status_code))
                # 在这里添加sleep语句，以等待一段时间再重试可能是个好主意
                time.sleep(3)

        # 如果for循环结束还没有返回，说明达到最大重试次数但仍未成功
        logging.error("尝试了 %d 次后，本企业向中心监管机构发起数据流转路径的POST请求仍未成功！", max_retries)
        return ""

    def pathEncryprtion(self, deleteNotifyTree, delrequest: dict, entry_time: str):
        """
        函数功能说明:
        对传入的deleteNotifyTree按照既定协议加密

        :param deleteNotifyTree: 向中心监管机构获取到的，经过格式化的数据流转树
               Tree对象
        :param delrequest: 删除请求，包含加密时所需要的信息
               delrequest:{
                "affairs_id": "00001",
                "user_id": "u00001",
                "info_id": "a1b2c3d4e5",
                "deleteMethod": "硬件删除",
                "deleteGranularity": "硬件删除"
                "from_bus_id":"b0001"  为了弥补我们系统demo无法根据ip地址查找区分父节点的缺陷
                }
        :param entry_time:时间，用做时间戳
               "2024-03-07 10:55:43"
        :return: 删除通知树（密文）
                 删除确认树（密文）待定
        """

        data = {
            "affairs_id": delrequest["affairs_id"],
            "user_id": delrequest["user_id"],
            "info_id": delrequest["info_id"],
            "deleteMethod": delrequest["deleteMethod"],
            "deleteGranularity": delrequest["deleteGranularity"]
        }
        print("加密内容:")
        print(data)
        plaintext = dumps(data)

        time_stamp = entry_time
        print("加密时间:")
        print(time_stamp)

        treetest = deleteNotifyTree
        print("加密树:")
        print(treetest)

        # 调用树的加密类
        encoder = MessageEncoder.Encoder()
        notify_tree, confirm_tree = encoder.treeEncode(treetest, time_stamp, plaintext)
        logging.info("删除通知树格式及内容如下:")
        print(notify_tree)
        logging.info("删除确认树格式及内容如下:")
        print(confirm_tree)

        # 解密测试
        # decoder = MessageDecoder.Decoder()
        # next_bus_ip_list, next_segment_tree_list = decoder.treeDecode('center', 'b1000', time_stamp, plaintext,
        #                                                               notify_tree)
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
        # aaa('center', 'b1000', time_stamp, plaintext, notify_tree)

        return notify_tree, confirm_tree

    def payloadEncryption(self, delnotifytree, plaintext):
        """
        函数功能说明：
        对传入的信息载荷进行IBBE加密

        :param delnotifytree:数据流转树，用于设置分组，把树上的每一个节点都加入到分组中，保证每个节点都可以解密
        :param plaintext: 信息载荷
        格式如下:
         {
        "affairs_id": "00001",
        "user_id": "u00001",
        "info_id": "a1b2c3d4e5",
        "deleteMethod": "硬件删除",
        "deleteGranularity": "硬件删除"
        }
        :return:  payloadIBBE 通过IBBE加密的信息载荷payload
        """

        # 调用辅助函数读取IBBE加密需要的 params, MSK, PK参数
        params, MSK, PK = IBBEKeyRead()

        # * 实例化对象
        encoder = MessageEncoder.Encoder()
        encoder.setParams(params.__str__())

        # 生成S参数 S参数是一个列表，包含此次删除通知中包含的所有节点ID
        S = collect_node_values(delnotifytree)
        logging.info("S列表如下:")
        print(S)

        # payload的IBBE加密
        plaintext = dumps(plaintext)
        payload = encoder.ibbeEncode((S, PK, MSK), plaintext)
        logging.info("payload加密内容如下:")
        print(payload)


        # 解密测试
        # decoder = MessageDecoder.Decoder()
        # decoder.setParams(params.__str__())
        # ID = 'b1000'
        # pairing1 = Pairing(params)
        # SK = Element(pairing1, G2, busid_to_IBBE_secret(ID))
        # pub_param = (S, SK, ID, PK)
        # try:
        #     newPlaintext = decoder.ibbeDecode(pub_param, payload)
        #     print(newPlaintext)
        # except Exception as e:
        #     print(e)

        # 说明
        # python函数可以直接返回元组格式，但是为了方便后续组成删除通知（包含三部分），且为了路由视图函数代码美观，在这里进行了序列化
        payload = list(payload)
        payload = json.dumps(payload)
        return payload




# 函数功能测试
# if __name__ == '__main__':
#     aaa = PathReqAndEncryption()
#     s = aaa.path_request("qwqwee", "safds")
#     print(s)
