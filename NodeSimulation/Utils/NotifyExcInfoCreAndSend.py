import datetime
import os
import csv
from NodeSimulation.Model.ConnectProxy import ConnectProxy


def NotifyExcInfoCreAndSend(plaintext, tree_plaintext, currentID, nextsendID):
    """
    函数说明：
      协助生成一下完整的删除通知发送异常信息（格式样例里的data）
      发送删除通知发送异常信息

    :param currentID: 当前节点
    :param nextsendID: 发送异常的接收节点
    :param plaintext:明文信息
        {
            'affairs_id': '00001',
             'user_id': 'u00001',
             'info_id': 'a1b2c3d4e5',
             'deleteMethod': 'yingjianshanchu',
             'deleteGranularity': 'age'
         }
    :param tree_plaintext:明文树，一个Tree对象
        b1000
            ├── b1001
            │   └── b1002
            └── b1003
                └── b1004

    :return: data 上报代理中心监管机构的异常信息
    """

    sourceDomainID = tree_plaintext.root

    lastDomainID = tree_plaintext.parent(currentID)
    if lastDomainID is not None:
        # 如果lastDomainID不是None，将其放入列表中
        lastDomainID = [lastDomainID.identifier]  # 注意，这里不需要迭代
    else:
        # 如果lastDomainID是None，则将其设为一个空列表或进行其他处理
        lastDomainID = []

    # nextDomainID = tree_plaintext.children(currentID)
    # if nextDomainID is not None:
    #     # 如果nextDomainID不是None，则进行迭代
    #     nextDomainID = [node.identifier for node in nextDomainID]
    # else:
    #     # 如果nextDomainID是None，则将其设为一个空列表或进行其他处理
    #     nextDomainID = []


    def get_path_to_node(tree, node_id):
        """
        获取从根节点到指定节点的路径（包括这两个节点）。
        :param tree: Tree对象
        :param node_id: 目标节点的ID
        :return: 包含路径上所有节点的列表
        """
        path = []
        current_node_id = node_id
        while current_node_id:  # 当current_node_id为None时停止循环，这意味着到达了根节点
            node = tree.get_node(current_node_id)  # 获取当前节点对象
            if node is None:
                raise ValueError("Node with ID '{}' not found in the tree.".format(current_node_id))
            path.append(node)  # 将当前节点添加到路径列表中
            current_node_id = tree.parent(current_node_id).identifier if tree.parent(current_node_id) else None

        return path[::-1]  # 返回反转的路径列表，以使其从根节点开始

    path = get_path_to_node(tree_plaintext, currentID)  # 获取从根节点到currentID的路径
    if path:
        # 如果path不是空，则进行迭代
        path = [node.identifier for node in path]
    else:
        # 如果path是空，则将其设为一个空列表或进行其他处理
        path = []


    # 获取当前时间，生成时间戳
    current_time = datetime.datetime.now()
    timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")

    data = {
        "DataType": 0x4020,
        "content": {
            "userID": plaintext['user_id'],
            "globalID": plaintext['info_id'],
            "sourceDomainID": sourceDomainID,
            "nextDomainID": nextsendID,
            "lastDomainID": lastDomainID,
            "deleteMethod": plaintext['deleteMethod'],
            "deleteDomainSet": path,
            "deleteNotify": f"在{timestamp}时间删除用户ID为{plaintext['user_id']}的身份证号信息{plaintext['info_id']}",
            "deleteNotifyCreateTime": timestamp,
            "deleteNotifyError": "403 Forbidden",
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






