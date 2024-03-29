"""
函数功能说明：
辅助解密从中心监管监管机构/上级企业接收到的删除通知信息

返回：解密后的明文信息
"""
import copy
import logging
import json
from json import dumps
from treelib import Tree, Node
from CenterSimulation.Utils.IBBEKeyRead import IBBEKeyRead, collect_node_values
from NodeSimulation.Model.protocol.Securityprotocol import MessageDecoder
from NodeSimulation.Model.protocol.Securityprotocol.protocol_utils.busid_to_secret import busid_to_secret, \
    busid_to_IBBE_secret
from pypbc import *
from CenterSimulation.Utils.Json2Tree import json2tree
from CenterSimulation.Model.PathReqAndEncryption import PathReqAndEncryption


def NotifyInfoDec(bus_id: str, busid_parent: str, EncInfolist: list):
    """
        函数功能说明:
        解密接收到的加密信息
        (可能来自代理中心监管机构，也可能来自前驱企业)
        :param busid_parent: 本节点的父节点
        :param bus_id:企业节点ID，在解密payload信息时候需要用到
        :param EncInfolist:一个信息列表, [删除通知树，时间戳，IBBE(payload),明文树]
        :return:  待定
    """

    # 日志打印信息设置
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # 提前将信息存储一下，用户后续返回
    # 进行深度拷贝，不然简单赋值没用，后续修改还是会把值影响到
    EncInfolistcopy = copy.deepcopy(EncInfolist)

    # 将删除通知树，IBBE密文，明文树loads一下，因为都进行了序列化
    # EncInfolist[0] = json.loads(EncInfolist[0])  # 删除通知树
    EncInfolist[2] = json.loads(EncInfolist[2])  # IBBE密文
    # EncInfolist[3] = json.loads(EncInfolist[3])  # 明文树

    logging.info("删除通知树:")
    print(EncInfolist[0])
    print(type(EncInfolist[0]))
    logging.info("时间戳：")
    print(EncInfolist[1])
    print(type(EncInfolist[1]))
    logging.info("IBBE密文：")
    print(EncInfolist[2])
    print(type(EncInfolist[2]))
    logging.info("明文树:")
    print(EncInfolist[3])
    print(type(EncInfolist[3]))
    # logging.info("父节点:")
    # print(EncInfolist[4])

    # 删除通知树
    tree = json2tree(EncInfolist[0])

    # 明文树
    tree_plaintext = json2tree(EncInfolist[3])

    logging.info("经过格式化之后的删除通知树:")
    print(tree)
    print(type(tree))

    logging.info("经过格式化之后的明文树:")
    print(tree_plaintext)
    print(type(tree_plaintext))

    # 计算S参数列表
    # S参数用于IBBE解密payload时作为参数
    S = collect_node_values(tree_plaintext)
    logging.info("S列表如下:")
    print(S)

    # IBBE解密过程
    # 参数获取
    params, MSK, PK = IBBEKeyRead()
    params = Parameters(params.__str__())
    ID = bus_id
    pairing1 = Pairing(params)
    SK = Element(pairing1, G2, busid_to_IBBE_secret(ID))

    # IBBE密文信息格式转换
    payload = tuple(EncInfolist[2])
    # print(payload)
    # print(type(payload))

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

    # todo 先不执行解密，因为老杀死进程
    # try:
    #     newPlaintext = decoder.ibbeDecode(pub_param, payload)
    # except Exception as e:
    #     print(e)
    #
    # # newPlaintext是str形式，需要转换回dict格式
    # newPlaintext = json.loads(newPlaintext)
    # print(newPlaintext)
    # print(type(newPlaintext))


    newPlaintext = {'affairs_id': '00001', 'user_id': 'u00001', 'info_id': 'a1b2c3d4e5', 'deleteMethod': 'yingjianshanchu',
             'deleteGranularity': 'age'}
    plaintext = json.dumps(newPlaintext)

    # 从删除通知中获取时间戳
    time = EncInfolist[1]


    print(f"当前节点{bus_id}解密输入参数：")
    print(busid_parent)
    print(bus_id)
    print(time)
    print(plaintext)
    print(tree)





    # 进行密文树解密
    next_bus_ip_list, next_segment_tree_list = decoder.treeDecode(busid_parent, bus_id, time, plaintext,
                                                                  tree)
    logging.info("后续节点列表:")
    print(next_bus_ip_list)
    logging.info("后续分发修改后的密文树（列表）:")
    for item in next_segment_tree_list:
        print(item)

    # 解密整棵树测试
    # def aaa(from_bus_id, to_bus_id, time_stamp, plaintext, segment_tree):
    #     print(from_bus_id + "--->" + to_bus_id)
    #     next_bus_ip_list, next_segment_tree_list = decoder.treeDecode(from_bus_id, to_bus_id, time_stamp, plaintext,
    #                                                                   segment_tree)
    #     print(next_bus_ip_list)
    #     print(next_segment_tree_list)
    #     for i, j in zip(next_bus_ip_list, next_segment_tree_list):
    #         if i == "center":
    #             break
    #         else:
    #             aaa(to_bus_id, i, time_stamp, plaintext, j)
    #
    # aaa('center', 'b1000', time, plaintext, tree)
    # next_bus_ip_list, next_segment_tree_list = []

    # 返回下一个用分发的列表，分发的树列表, 明文, 密文（后续进行修改，然后继续分发）
    return next_bus_ip_list, next_segment_tree_list, newPlaintext, EncInfolistcopy, tree_plaintext
