"""
此py文件定义节点（企业）的类
类中包含的函数的具体功能：
    1.删除意图解析
    2.自动触发（当前考虑计时触发）
    3.按需触发
    4.删除通知生成
    5.通知范围确定
    6.指令分解分发
    7.通知接收验证
    8.通知完备性验证
    9.通知与确认存证
说明：
    在具体函数的功能实现过程中，会构建多个衍生的功能类，协助各个函数完成对应的功能
    为了使得项目逻辑明晰，相关的工具类会放置在utils文件夹中
"""
import copy
import logging
import threading
import csv
import os
import hashlib
from threading import Thread
from NodeSimulation.Utils.demand_trigger_process import demand_tri_pro
from NodeSimulation.Utils.count_trigger_process import count_tri_pro
from NodeSimulation.Utils.timer_trigger_process import time_tri_pro
from NodeSimulation.Model.ConnectProxy import ConnectProxy
from NodeSimulation.Model.ConnectSysDel import ConnectSysDel
from NodeSimulation.Model.DelNotifySend import DelNotifySend
from NodeSimulation.Model.protocol.Securityprotocol.protocol_utils.sm3_hmac import hmac
from NodeSimulation.Utils.delNotifyAckBack import delNotifyAckBack


class EnterpriseNode:
    # 日志打印信息设置
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # 节点（企业）类初始化函数
    def __init__(self, Bus_id):
        self.Bus_id = Bus_id

    # 删除意图解析函数
    def del_intention_parsing(self, delintention):
        """
        接收到的数据参数是一个字典，内容为删除意图
        :param:
        delintention = {
            "affairs_id": "00001",
            "user_id": "u00001",
            "deleteGranularity": "age",
            "info_id": "a1b2c3d4e5",
            "source_bus_id": "b00001",
            "time_limit": 20,     #时间限制为可选字段，不是每次内容都有，”“空字符表示没有时间显示
            "count_limit": 0,   #次数限制为可选字段，不是每次内容都有,0表示没有次数限制
            "deleteMethod": "硬件删除"
        }

        函数返回值为删除请求
        如果解析结果为计时触发，也会开启新的线程进行计时，没有实际返回值内容，直接return
        直接在删除意图解析函数中调用数据存储相关函数存储初始数据在数据库中
        :return:
        delrequest = {
            "affairs_id": "00001",
            "user_id": "u00001",
            "info_id": "a1b2c3d4e5",
            "deleteMethod": "硬件删除",
            "deleteGranularity": "age",
            "from_bus_id:"1000"  # 为了弥补我们系统demo无法根据IP来进行节点区分，实际中是可行的
        }
        """

        # 计时触发，计次触发，只能二选一执行
        # 计时触发（自动触发之一）
        if delintention["time_limit"] and delintention["count_limit"] == 0:
            # 计时触发的方式，启动一个线程，进行计时，计时结束之后，给节点的处理监听路由发送不带有时间限制的删除意图请求即可
            # todo 处理逻辑，计时结束之后再发起删除意图请求，不带有时间限制和次数限制的为按需触发
            # 传入的参数为 删除意图 时间限制

            # 这里启动的多线程处理，默认非守护线程
            """
            非守护线程与守护线程的区别：
                守护线程当主线程结束时，守护线程会被立即终止。
            守护线程通常用于在后台运行的服务和任务，其生命周期依赖于主线程。
            它们对于那些不需要显式停止操作的任务很有用，因为它们会随着主线程的结束而自动结束。
                非守护线程不会随着主线程的结束而终止。
            主线程结束后，非守护线程会继续运行直到它们的任务完成。
            如果程序中所有线程都是非守护线程，Python解释器将会等待所有线程完成后才退出
            """

            logging.info("已经成功解析删除意图为“计时触发”")

            # 计时结束后，执行此函数
            def timer_action():
                logging.info("计时触发成功,后续程序开始执行·····")
                time_tri_pro(delintention, delintention["time_limit"], self.Bus_id)

            # 判断时间限制参数是否包含非数字字符
            time_number = 0
            try:
                time_number = int(delintention["time_limit"])
            except ValueError:
                logging.warning('计时时间限制输入格式不规范，无法解析')

            # 设置计时器，设置得时间满足后执行 timer_action 函数
            timer = threading.Timer(time_number, timer_action)
            # 启动计时器
            timer.start()

            # 对于计时触发，无返回实值
            return

        # 计次触发（自动触发之一）
        elif not delintention["time_limit"] and delintention["count_limit"] != 0:
            logging.info("已经成功解析删除意图为“计次触发”")
            delrequest = count_tri_pro(delintention, delintention["count_limit"], self.Bus_id)
            delrequest["from_bus_id"] = self.Bus_id
            return delrequest

        # 按需触发
        elif not delintention["time_limit"] and delintention["count_limit"] == 0:
            logging.info("已经成功解析删除意图为“按需触发”")
            delrequest = demand_tri_pro(delintention, self.Bus_id)
            delrequest["from_bus_id"] = self.Bus_id
            return delrequest

        # elif "time_limit" not in delintention and "count_limit" not in delintention:
        #     logging.info("已经成功解析删除意图为“按需触发”")
        #     delrequest = demand_tri_pro(delintention, self.Bus_id)
        #     return delrequest

        # 输入格式不规范，无法解析
        else:
            logging.warning('删除意图输入格式不规范，无法解析')
            # 删除意图解析输入格式不规范,无返回实值
            return False

    # 删除通知范围确定与删除通知生成函数
    def del_Notify_scopeAndgenerate(self, delrequest):
        """
        函数说明：
        删除通知范围确定，根据特定信息与中心监管机构交互，获取删除通知树
        此外，代理中心机构还会生成IBBE加密的信息载荷
        同时，还会返回时间戳

        # todo 为了后续适配确定性删除系统以及删除效果评测系统，明文树与密文树均保留
        :return: 删除通知（密文）+ 数据流转树（明文，为了适配） + "from_bus_id"(为了弥补系统demo无法根据ip区分不同的节点)
        # 删除通知的组成：删除通知树 + 时间戳 + 信息载荷
        """

        # 获取当前文件的绝对路径
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # 设置相对于当前文件的路径
        current_folder = os.path.join(current_dir, '..', 'Resource')
        current_file_ID = 'ID.csv'
        current_file_centerID = 'ProxyCenterID'

        # 组合并规范化路径
        current_path_ID = os.path.normpath(os.path.join(current_folder, current_file_ID))
        current_path_centerID = os.path.normpath(os.path.join(current_folder, current_file_centerID))

        # 向代理中心监管机构请求删除流转路径
        # 读取中心监管机构的ID
        with open(current_path_centerID, "r") as f:
            centerID = f.read()

        # 根据ID查询信息表获取IP和port
        with open(current_path_ID, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['ID'] == centerID:  # 默认代理中心监管机构的ID是b1100
                    port = row['port']
                    ip = row['IP']

        # 向代理中心监管机构发请求
        connectproxy = ConnectProxy(ip, port)

        # 返回删除通知密文
        ciphertext = connectproxy.delNotifyReq(delrequest)
        return ciphertext

    # 删除指令分解与分发
    def del_instruction_decAnddis(self, delNotify, tree_plaintext):
        """
        函数说明:
        根据删除通知内容，和删除通知树（明文），与确定性删除系统交互，发送删除指令
        :param delNotify: 删除通知内容
        :param tree_plaintext: 明文删除通知树
        :return:
        """
        # 请求路由获取(获取确定性删除系统的url)
        # 获取当前文件的绝对路径
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # 设置相对于当前文件的路径
        config_folder = os.path.join(current_dir, '..', 'Resource')
        config_file = 'SystemInfoDelUrl'

        # 组合并规范化路径
        config_path = os.path.normpath(os.path.join(config_folder, config_file))
        with open(config_path, "r") as f:
            url = f.read()

        # 调用与确定性删除系统交互的类
        connectsysdel = ConnectSysDel(url)

        # 构建生成删除指令
        delInstruction = connectsysdel.buildDelIns(delNotify, tree_plaintext)

        # 删除指令发送
        response = connectsysdel.sendDelIns(delInstruction)
        logging.info(response)

    # 删除通知生成
    def del_Notify_generateAndsend(self, next_bus_id_list, next_segment_tree_list, EncInfolist, currentID, plaintext, tree_plaintext, busid_parent):

        """
        函数说明：
            不仅负责删除通知的生成，同时还负责给后续企业发送删除通知
            如果后续节点为空（当前节点为叶子节点，生成删除通知确认，给父节点回传，由中心监管机构（代理）验证）

        :param next_bus_id_list: 后续节点列表[list]
        :param next_segment_tree_list: 已经修改好的删除通知树[list]
        :param EncInfolist: 删除通知密文[list]
        :param currentID: 本节点的ID(str)
        :param busid_parent: 本节点的父节点的ID，用户删除通知确认消息回传寻址
        :param plaintext: 通知明文信息，协助生成删除通知异常信息
        :param tree_plaintext: 明文树，协助生成删除通知异常信息

        :return:
        """

        # 读取后续节点列表
        # 正常情况
        # 后续列表不为空
        if next_bus_id_list:
            logging.info(f"当前企业{currentID}对于本条信息的后续'子节点企业'为{next_bus_id_list}")

            # 此处的if判断是否为叶子节点，满足if条件说明是叶子节点
            if len(next_bus_id_list) == 1 and next_bus_id_list[0] == 'center':
                logging.info("经过解密判断，后续节点为空！！！！！")
                logging.info("开始生成删除通知确认内容，进行回传···")

                # 注：生成删除通知确认的时候要和代理中心监管机构生成删除通知确认树对应

                # 第一步，生成删除通知确认消息
                # dict_ack = {}
                # DelConfirm = {}
                # for tree in next_segment_tree_list:
                #     dict_ack[currentID] = [tree.root]
                dict_ack = {
                    currentID: []
                }
                DelConfirm = {}
                for tree in next_segment_tree_list:
                    dict_ack[currentID].append(tree.root)

                DelConfirm["affairs_id"] = plaintext["affairs_id"]
                DelConfirm["DelConfirmSignatureDict"] = dict_ack
                logging.info("删除通知确认内容为:")
                print(DelConfirm)
                # 第二步，回传删除通知确认消息
                delNotifyAckBack(busid_parent, DelConfirm, plaintext, self.Bus_id)

                return

            # 下面执行的是非叶子节点时执行的的内容，继续分发删除通知内容
            # 在这里把删除通知中要加入的from_bus_id加入
            # 但是要判断一下，之前是否已经在第4个位置添加过内容，添加过需要覆盖，没添加过添加
            # 这里设定了删除通知列表长度为5，其实缺乏一些健壮性，如果后续更改删除通知内容，这里要修改
            if len(EncInfolist) == 4:
                EncInfolist.append(self.Bus_id)
            else:
                EncInfolist[4] = self.Bus_id

            delNotice = EncInfolist

            # 调用发送类发送消息
            delnotifysend = DelNotifySend(next_bus_id_list, next_segment_tree_list, delNotice, plaintext, tree_plaintext, currentID)
            delnotifysend.runtest()

        # 异常情况
        else:
            logging.warning("解密出的后续子节点列表错误，请检查内容！内容如下:")
            for i in next_bus_id_list:
                print(i)





# 函数功能测试
from NodeSimulation.Utils.NotifyInfoDecryption import NotifyInfoDec
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

if __name__ == '__main__':
    bus_id = 'b1000'
    busid_parent = 'center'
    aaa = EnterpriseNode("b1001")
    delrequest = {
        "affairs_id": "00001",
        "user_id": "u00001",
        "info_id": "a1b2c3d4e5",
        "deleteMethod": "yingjianshanchu",
        "deleteGranularity": "age",
        "from_bus_id": "b1000"
        # 为了弥补我们系统demo无法根据IP来进行节点区分，实际中是可行的
    }

    # aaa = ConnectProxy("127.0.0.1", 20100)
    # s = aaa.delNotifyReq(delrequest)

    s = aaa.del_Notify_scopeAndgenerate(delrequest)
    s = json.loads(s)
    print(s)

    NotifyInfoDec(bus_id, busid_parent, s)

    # EncInfolist = s
    #
    #
    # # NotifyInfoDec(bus_id, busid_parent, s)
    # # 将删除通知树，IBBE密文，明文树loads一下，因为都进行了序列化
    # # EncInfolist[0] = json.loads(EncInfolist[0])  # 删除通知树
    # EncInfolist[2] = json.loads(EncInfolist[2])  # IBBE密文
    # # EncInfolist[3] = json.loads(EncInfolist[3])  # 明文树
    #
    # logging.info("删除通知树:")
    # print(EncInfolist[0])
    # print(type(EncInfolist[0]))
    # logging.info("时间戳：")
    # print(EncInfolist[1])
    # print(type(EncInfolist[1]))
    # logging.info("IBBE密文：")
    # print(EncInfolist[2])
    # print(type(EncInfolist[2]))
    # logging.info("明文树:")
    # print(EncInfolist[3])
    # print(type(EncInfolist[3]))
    #
    # # 删除通知树
    # tree = json2tree(EncInfolist[0])
    #
    # # 明文树
    # tree_plaintext = json2tree(EncInfolist[3])
    #
    # logging.info("经过格式化之后的删除通知树:")
    # print(tree)
    # print(type(tree))
    #
    # logging.info("经过格式化之后的明文树:")
    # print(tree_plaintext)
    # print(type(tree_plaintext))
    #
    # # 计算S参数列表
    # # S参数用于IBBE解密payload时作为参数
    # S = collect_node_values(tree_plaintext)
    # logging.info("S列表如下:")
    # print(S)
    #
    # # IBBE解密过程
    # # 参数获取
    # params, MSK, PK = IBBEKeyRead()
    # params = Parameters(params.__str__())
    # ID = bus_id
    # pairing1 = Pairing(params)
    # SK = Element(pairing1, G2, busid_to_IBBE_secret(ID))
    #
    # # IBBE密文信息格式转换
    # payload = tuple(EncInfolist[2])
    # print(payload)
    # print(type(payload))
    #
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
    #
    # # newPlaintext是str形式，需要转换会dict格式
    # newPlaintext = json.loads(newPlaintext)
    # print(newPlaintext)
    # print(type(newPlaintext))
    #
    # # plain = {'affairs_id': '00001', 'user_id': 'u00001', 'info_id': 'a1b2c3d4e5', 'deleteMethod': 'yingjianshanchu',
    # #          'deleteGranularity': 'age'}
    # plaintext = json.dumps(newPlaintext)
    #
    # time = EncInfolist[1]
    #
    # # def aaa(from_bus_id, to_bus_id, time_stamp, plaintext, segment_tree):
    # #     print(from_bus_id + "--->" + to_bus_id)
    # #     next_bus_ip_list, next_segment_tree_list = decoder.treeDecode(from_bus_id, to_bus_id, time_stamp, plaintext,
    # #                                                                   segment_tree)
    # #     print(next_bus_ip_list)
    # #     print(next_segment_tree_list[0])
    # #     # for i, j in zip(next_bus_ip_list, next_segment_tree_list):
    # #     #     if i == "center":
    # #     #         break
    # #     #     else:
    # #     #         aaa(to_bus_id, i, time_stamp, plaintext, j)
    # #
    # # aaa(busid_parent, bus_id, time, plaintext, tree)
    #
    # next_bus_ip_list, next_segment_tree_list = decoder.treeDecode(busid_parent, bus_id, time, plaintext,
    #                                                               tree)
    # logging.info("后续节点列表:")
    # print(next_bus_ip_list)
    # logging.info("后续分发修改后的密文树（列表）:")
    # for item in next_segment_tree_list:
    #     print(item)
