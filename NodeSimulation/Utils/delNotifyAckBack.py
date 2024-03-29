"""
函数说明：
    实现删除通知确认消息回传
"""
import os
import csv
import requests
import json
import logging
import time
from NodeSimulation.Utils.AckExcInfoCreAndSend import AckExcInfoCreAndSend


def delNotifyAckBack(busid_parent, dict_ack, plaintext, currentID):
    """

    :param busid_parent: 当前节点的父节点ID，用于回传寻址
    :param dict_ack: 删除通知确认消息的内容
    :param plaintext: 明文信息，用于异常上报
    :param currentID: 当前节点ID，用于异常上报
    :return:
    """
    # 日志打印信息设置
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # 获取当前文件的绝对路径
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 设置相对于当前文件的路径
    current_folder = os.path.join(current_dir, '..', 'Resource')
    current_file_ID = 'ID.csv'
    current_file_centerID = 'ProxyCenterID'

    # 组合并规范化路径
    current_path_ID = os.path.normpath(os.path.join(current_folder, current_file_ID))
    current_path_centerID = os.path.normpath(os.path.join(current_folder, current_file_centerID))

    # 删除通知确认回传路由构建
    if busid_parent == 'center':
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
        url = f"http://{ip}:{port}/center/receive_confirm"
    else:
        # 根据ID查询信息表获取IP和port
        with open(current_path_ID, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['ID'] == busid_parent:
                    port = row['port']
                    ip = row['IP']
        url = f"http://{ip}:{port}/enterprise/receive_enter_confirm"

    print(url)

    # 删除通知确认回传内容序列化
    reqTree = json.dumps(dict_ack)

    max_retries = 3  # 最大重试次数
    for attempt in range(max_retries):
        response = requests.post(url, json=reqTree)
        if response.status_code == 200:
            logging.info(f"向父节点{busid_parent}回传删除通知确认信息成功！")
            logging.info(response.text)
            return response.text
        else:
            logging.error(f"尝试 #{attempt + 1}: 向父节点{busid_parent}回传删除通知确认信息失败！")
            logging.error("响应状态码: " + str(response.status_code))
            # 在这里添加sleep语句，以等待一段时间再重试可能是个好主意
            time.sleep(3)

    # 如果for循环结束还没有返回，说明达到最大重试次数但仍未成功
    logging.error(f"尝试了 %d 次后，本企业向父节点{busid_parent}回传删除通知确认信息仍未成功！",
                  max_retries)

    # todo 这里进行删除通知确认回送异常返回
    AckExcInfoCreAndSend(plaintext, currentID, busid_parent, dict_ack)
