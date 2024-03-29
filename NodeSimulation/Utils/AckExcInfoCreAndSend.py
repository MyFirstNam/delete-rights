import datetime
import os
import csv
from NodeSimulation.Model.ConnectProxy import ConnectProxy


def AckExcInfoCreAndSend(plaintext, currentID, CurrentParentID, Delconfirm):
    """
    函数说明：
      协助生成一下完整的删除通知确认回传异常信息（格式样例里的data）
      发送删除通知确认回传异常信息

    :param currentID: 当前节点
    :param CurrentParentID: 当前节点的父亲节点
    :param plaintext:明文信息
        {
            'affairs_id': '00001',
             'user_id': 'u00001',
             'info_id': 'a1b2c3d4e5',
             'deleteMethod': 'yingjianshanchu',
             'deleteGranularity': 'age'
         }

    :param Delconfirm: 删除通知确认消息合集

    :return: data 上报代理中心监管机构的异常信息
    """

    data = {
        "DataType": 0x4021,
        "content": {
            "userID": plaintext['user_id'],
            "globalID": plaintext['info_id'],
            "deleteNotifyAck": f"域{currentID}向域{CurrentParentID}返回删除通知确认",
            "sourceDomainID": CurrentParentID,
            "dictAck": Delconfirm,
            "deleteNotifyAckError": "403 Forbidden"
        }
    }
    print(data)

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
    connectproxy.exceptionInfoSend(data)

    return
