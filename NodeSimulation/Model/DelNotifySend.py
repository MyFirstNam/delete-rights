"""
类功能说明：
    协助实现异步发送删除通知的内容
    此类负责根据有几个子节点，负责启动几个异步函数，然后发送对应内容
"""

import asyncio
import copy
import json
import csv
import logging
from aiohttp import ClientError, ClientSession
import os
from treelib import Tree
from NodeSimulation.Utils.NotifyExcInfoCreAndSend import NotifyExcInfoCreAndSend

# 因测试导入
from CenterSimulation.Utils.IBBEKeyRead import IBBEKeyRead, collect_node_values
from NodeSimulation.Model.protocol.Securityprotocol import MessageDecoder
from pypbc import *


class DelNotifySend:
    def __init__(self, next_bus_id_list: list, next_segment_tree_list: list, delNotice: list, plaintext: dict,
                 tree_plaintext, currentID: str):
        """

        :param next_bus_id_list: 后续发送列表
        :param next_segment_tree_list:  后续发送删除通知树列表
        :param delNotice: 密文内容[密文删除通知树，时间戳，密文内容，明文树，from_bus_id]

        :param plaintext: 通知明文信息，协助生成删除通知异常信息
        :param tree_plaintext: 明文树，协助生成删除通知异常信息 Tree对象
        :param currentID: 当前节点，协助生成删除通知异常信息
        """
        self.nextNode = next_bus_id_list
        self.nextsegmentree = next_segment_tree_list
        self.delNotice = delNotice

        self.plaintext = plaintext
        self.tree_plaintext = tree_plaintext
        self.currentID = currentID

    async def send_post_request(self, ip, port, delNotice, nextsendID):
        """
        执行异步发送
        :param ip: 发送地址IP
        :param port: 发送地址port
        :param delNotice: 发送内容
        :return:
        """

        # # 这里进行测试是为了在正常的情况下上报异常信息
        # # 在这里加工一下异常上报信息
        # exceptioninfo = NotifyExcInfoCreate(self.plaintext, self.tree_plaintext, self.currentID)


        delNotice = json.dumps(delNotice)
        data = copy.deepcopy(delNotice)
        url = f"http://{ip}:{port}/enterprise/receive_enter"

        max_retries = 3  # 最大重试次数
        async with ClientSession() as session:
            for attempt in range(max_retries):
                try:
                    async with session.post(url, json=data) as response:
                        response.raise_for_status()
                        text = await response.text()
                        logging.info("——————————————————————————————删除通知分发——————————————————————————————")
                        logging.info(f"给企业对应的网络地址 {url} 发送删除通知成功!")
                        logging.info(text)
                        return text
                except ClientError as e:
                    logging.info(f"第 {attempt + 1} 次 HTTP 请求失败，给子节点发送删除通知失败！错误详情:{e}")
                except asyncio.TimeoutError:
                    logging.info(f"第 {attempt + 1} 次请求超时")

            logging.info(f"系统尝试发送 {max_retries} 次后，仍未发送成功！")

            # todo 在这里进行删除通知发送失败异常上报

            # 在这里加工一下异常上报信息
            # 同时还负责发送
            NotifyExcInfoCreAndSend(self.plaintext, self.tree_plaintext, self.currentID, nextsendID)

            return None

    async def senddelNotify(self):
        """
        函数说明：
            此函数中的IP和port通过子节点的唯一标识符ID查询而来，循环添加
            同时还得循环修改删除通知内容（因为发给每一个企业的删除通知树是不一样的）
        :return:
        """

        # 获取当前文件的绝对路径
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # 设置相对于当前文件的路径
        current_folder = os.path.join(current_dir, '..', 'Resource')
        current_file_ID = 'ID.csv'

        # 组合并规范化路径
        current_path_ID = os.path.normpath(os.path.join(current_folder, current_file_ID))

        # 初始化异步任务列表
        newdelNoticeList = []
        for item, notifyTree in zip(self.nextNode, self.nextsegmentree):
            with open(current_path_ID, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row['ID'] == item:  # 默认中心监管机构的ID是b1100
                        port = row['port']
                        ip = row['IP']
                        break

            # 进行深度拷贝，不然简单赋值没用，后续修改还是会把值影响到
            delNotice = copy.deepcopy(self.delNotice)
            print(item)
            print(notifyTree)

            # # 解密树测试
            # params, MSK, PK = IBBEKeyRead()
            # params = Parameters(params.__str__())
            # decoder = MessageDecoder.Decoder()
            # decoder.setParams(params.__str__())
            # newPlaintext = {'affairs_id': '00001', 'user_id': 'u00001', 'info_id': 'a1b2c3d4e5',
            #                 'deleteMethod': 'yingjianshanchu',
            #                 'deleteGranularity': 'age'}
            # plaintext = json.dumps(newPlaintext)
            #
            # # 从删除通知中获取时间戳
            # time = "12345678"
            # bus_id = item
            # tree = notifyTree
            # busid_parent = delNotice[4]
            # # 进行密文树解密
            # next_bus_ip_list, next_segment_tree_list = decoder.treeDecode(busid_parent, bus_id, time, plaintext,
            #                                                               tree)
            # logging.info("后续节点列表:")
            # print(next_bus_ip_list)
            # logging.info("后续分发修改后的密文树（列表）:")
            # for item in next_segment_tree_list:
            #     print(item)

            # 把删除通知中的删除通知树更新
            # 把树序列化
            delNotice[0] = notifyTree.to_json(sort=False)
            newdelNoticeList += [(ip, port, delNotice, item)]
        coroutines = [asyncio.create_task(self.send_post_request(x, i, j, t)) for x, i, j, t in newdelNoticeList]
        await asyncio.wait(coroutines)

    def runtest(self):
        asyncio.run(self.senddelNotify())
