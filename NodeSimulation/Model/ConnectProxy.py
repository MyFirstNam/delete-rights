"""
类功能说明:
负责企业节点与代理中心机构的全部通信，具体如下：
1.向中心监管机构请求数据流转树（实际返回的已经是删除通知的各部分内容）
2.向中心监管机构推送日志内容
3.向中心监管机构推送异常信息内容
"""
import logging
import requests
import time


class ConnectProxy:
    # 日志打印信息设置
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def delNotifyReq(self, delrequest):
        """
        函数说明：
        向代理中心监管机构请求数据流转树
        实际返回的内容为删除通知（密文树，时间戳等）
        :param delrequest: 请求内容
               delrequest = {
                "affairs_id": "00001",
                "user_id": "u00001",
                "info_id": "a1b2c3d4e5",
                "deleteMethod": "硬件删除",
                "deleteGranularity": "age",
                "from_bus_id:"1000"
               }
        :return:
        """

        logging.info(
            f'向代理中心监管机构请求info为{delrequest["info_id"]}的信息流转记录，此次事务的id为{delrequest["affairs_id"]}')

        # 请求路由构建
        url = f"http://{self.ip}:{self.port}/center/receive_path"
        print(url)
        # 请求内容序列化
        reqTree = json.dumps(delrequest)

        max_retries = 3  # 最大重试次数
        for attempt in range(max_retries):
            response = requests.post(url, json=reqTree)
            if response.status_code == 200:
                logging.info("向代理中心监管机构发起数据流转路径（获取删除通知）的POST请求成功！")
                return response.text
            else:
                logging.error(f"尝试 #{attempt + 1}: 向中心监管机构发起数据流转路径（获取删除通知）的POST请求失败！")
                logging.error("响应状态码: " + str(response.status_code))
                # 在这里添加sleep语句，以等待一段时间再重试可能是个好主意
                time.sleep(3)

        # 如果for循环结束还没有返回，说明达到最大重试次数但仍未成功
        logging.error("尝试了 %d 次后，本企业向中心监管机构发起数据流转路径（获取删除通知）的POST请求仍未成功！",
                      max_retries)
        return ""

    def exceptionInfoSend(self, exceptionInfo):
        """
        函数说明：
            向代理中心监管机构转发删除通知/删除通知确认异常信息

        :param exceptionInfo: 异常信息内容
              # 这里格式不固定，但是固定的是是一个dict,有可能是删除通知失败异常，也可能是删除通知确认失败异常
        :return:
        """

        # 请求路由构建
        url = f"http://{self.ip}:{self.port}/center/receive_exception"
        print(url)
        # 请求内容序列化
        reqTree = json.dumps(exceptionInfo)

        max_retries = 3  # 最大重试次数
        for attempt in range(max_retries):
            response = requests.post(url, json=reqTree)
            if response.status_code == 200:
                logging.info("向代理中心监管机构发送异常信息的POST请求成功！")
                logging.info(response.text)
                return response.text
            else:
                logging.error(f"尝试 #{attempt + 1}: 向代理中心监管机构发送异常信息的POST请求失败！")
                logging.error("响应状态码: " + str(response.status_code))
                # 在这里添加sleep语句，以等待一段时间再重试可能是个好主意
                time.sleep(3)

        # 如果for循环结束还没有返回，说明达到最大重试次数但仍未成功
        logging.error("尝试了 %d 次后，本企业向代理中心监管机构发送异常信息的POST请求仍未成功！",
                      max_retries)
        return ""















# 测试____________________________________________________________________________________________________
import json
from json import dumps
from treelib import Tree, Node
from CenterSimulation.Utils.IBBEKeyRead import IBBEKeyRead, collect_node_values
from NodeSimulation.Model.protocol.Securityprotocol import MessageDecoder
from NodeSimulation.Model.protocol.Securityprotocol.protocol_utils.busid_to_secret import busid_to_secret, busid_to_IBBE_secret
from pypbc import *
from CenterSimulation.Utils.Json2Tree import json2tree
from CenterSimulation.Model.PathReqAndEncryption import PathReqAndEncryption

# 函数功能测试
if __name__ == '__main__':
    aaa = ConnectProxy("127.0.0.1", 20100)
    delrequest = {
        "affairs_id": "00001",
        "user_id": "u00001",
        "info_id": "a1b2c3d4e5",
        "deleteMethod": "yingjianshanchu",
        "deleteGranularity": "age",
        "from_bus_id": "b1000"
        # 为了弥补我们系统demo无法根据IP来进行节点区分，实际中是可行的
    }
    s = aaa.delNotifyReq(delrequest)
    # 首先把接收到的数据loads一下，因为return的时候执行了jsonify
    # loads之后变成了一个列表
    s = json.loads(s)
    print(type(s))




    # 然后将删除通知树，IBBE密文，明文树loads一下，因为都进行了序列化
    # s[0] = json.loads(s[0])  # 删除通知树
    s[2] = json.loads(s[2])  # IBBE密文
    # s[3] = json.loads(s[3])  # 明文树
    print("删除通知树:")
    print(s[0])
    print(type(s[0]))
    print("时间戳：")
    print(s[1])
    print(type(s[1]))
    print("IBBE密文：")
    print(s[2])
    print(type(s[2]))
    print("明文树:")
    print(s[3])
    print(type(s[3]))

    # def add_node_from_dict(node_dict, tree, parent=None):
    #     # 遍历字典中的每个节点
    #     for node_id, content in node_dict.items():
    #         # 创建当前节点
    #         tree.create_node(tag=node_id, identifier=node_id, parent=parent)
    #         # 如果存在子节点，递归添加子节点
    #         if 'children' in content and content['children']:
    #             for child in content['children']:
    #                 add_node_from_dict(child, tree, parent=node_id)
    #
    #
    # def build_tree(data_dict):
    #     tree = Tree()
    #     # 从提供的字典开始构建树
    #     add_node_from_dict(data_dict, tree)
    #     return tree
    #
    #
    # # 重建树
    # tree = build_tree(s[0])
    # tree1 = build_tree(s[3])
    # # 打印树以验证
    # print(tree)
    # print(tree1)

    # tree = Tree()
    #
    # def add_nodes(parent_id, children):
    #     for child in children:
    #         if isinstance(child, dict):  # 如果子节点是字典，表示它有进一步的子节点
    #             for child_id, grandchild in child.items():
    #                 if "children" in grandchild:  # 如果有更深层的子节点
    #                     tree.create_node(tag=child_id, identifier=child_id, parent=parent_id)
    #                     add_nodes(child_id, grandchild["children"])
    #                 else:  # 如果没有更深层的子节点，直接添加
    #                     tree.create_node(tag=child_id, identifier=child_id, parent=parent_id)
    #         else:  # 如果子节点不是字典，表示它是叶子节点
    #             tree.create_node(tag=child, identifier=child, parent=parent_id)
    #
    #
    # # 初始化根节点
    # root_id = 'root'
    # tree.create_node(tag=root_id, identifier=root_id)
    #
    # # 从根节点开始添加所有子节点
    # add_nodes(root_id, s[0][root_id]['children'])
    #
    # print(tree)

    tree = json2tree(s[0])
    tree1 = json2tree(s[3])
    print(tree)
    print(type(tree))
    print(tree1)
    print(type(tree1))

    S = collect_node_values(tree1)
    logging.info("S列表如下:")
    print(S)

    # def aaa(from_bus_id, to_bus_id, time_stamp, plaintext, segment_tree):
    #     print(from_bus_id + "--->" + to_bus_id)
    #     next_bus_ip_list, next_segment_tree_list = decoder.treeDecode(from_bus_id, to_bus_id, time_stamp,plaintext, segment_tree)
    #     for i, j in zip(next_bus_ip_list, next_segment_tree_list):
    #         if i == "center":
    #             break
    #         else:
    #             aaa(to_bus_id, i, time_stamp, plaintext, j)
    #
    # aaa('center', 'b1000',time_stamp, plaintext, segment_tree)

    params, MSK, PK = IBBEKeyRead()
    params = Parameters(params.__str__())

    ID = 'b1000'
    pairing1 = Pairing(params)
    SK = Element(pairing1, G2, busid_to_IBBE_secret(ID))

    ID = 'b1000'
    payload = tuple(s[2])
    print(payload)
    print(type(payload))

    Hdry = payload[0]
    for i, (Hdr, y) in enumerate(Hdry):
        Hdr[0] = Element(pairing1, G1, Hdr[0])
        Hdr[1] = Element(pairing1, G2, Hdr[1])
        Hdry[i] = (Hdr, y)

    payload_list = list(payload)
    payload_list[0] = Hdry
    payload = tuple(payload_list)
    pub_param = (S, SK, ID, PK)

    decoder = MessageDecoder.Decoder()
    decoder.setParams(params.__str__())
    newPlaintext = ""
    try:
        newPlaintext = decoder.ibbeDecode(pub_param, payload)
    except Exception as e:
        print(e)

    # newPlaintext是str形式，需要转换会dict格式
    newPlaintext = json.loads(newPlaintext)
    print(newPlaintext)
    print(type(newPlaintext))

    # plain = {'affairs_id': '00001', 'user_id': 'u00001', 'info_id': 'a1b2c3d4e5', 'deleteMethod': 'yingjianshanchu',
    #          'deleteGranularity': 'age'}
    plaintext = json.dumps(newPlaintext)


    # plaintext = newPlaintext

    def aaa(from_bus_id, to_bus_id, time_stamp, plaintext, segment_tree):
        print(from_bus_id + "--->" + to_bus_id)
        next_bus_ip_list, next_segment_tree_list = decoder.treeDecode(from_bus_id, to_bus_id, time_stamp, plaintext,
                                                                      segment_tree)
        print(next_bus_ip_list)
        print(next_segment_tree_list[0])
        print(next_segment_tree_list[1])
        # for i, j in zip(next_bus_ip_list, next_segment_tree_list):
        #     if i == "center":
        #         break
        #     else:
        #         aaa(to_bus_id, i, time_stamp, plaintext, j)


    time = s[1]
    print(tree)
    aaa('center', 'b1000', time, plaintext, tree)
