import os
from pypbc import *
from CenterSimulation.Model.SecurityProtocol.protocol_utils.gen_tree import gen_tree
from CenterSimulation.Model.SecurityProtocol.protocol_utils.busid_to_secret import busid_to_IBBE_secret


# 辅助读取IBBE加密需要的参数
def IBBEKeyRead():
    # 获取当前文件的绝对路径
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 设置相对于当前文件的路径
    config_folder = os.path.join(current_dir, '../', 'Resource/IBBE_params')
    config_file_params = 'IBBE_params.txt'

    # 组合并规范化路径
    config_path_params = os.path.normpath(os.path.join(config_folder, config_file_params))

    with open(config_path_params, "r") as f:
        params = f.read()

    params = Parameters(params)
    pairing1 = Pairing(params)

    config_file_MSK = 'IBBE_MSK.txt'
    # 组合并规范化路径
    config_path_MSK = os.path.normpath(os.path.join(config_folder, config_file_MSK))

    MSK = []
    with open(config_path_MSK, "r") as f:
        for i in range(2):
            if i == 0:
                value = f.readline().replace('\n', '')
                MSK.append(Element(pairing1, G1, value=value))
            elif i == 1:
                value = f.readline().replace('\n', '')
                t = Element(pairing1, Zr, value=int(value[2:], 16))
                MSK.append(t)

    config_file_PK = 'IBBE_PK.txt'
    # 组合并规范化路径
    config_path_PK = os.path.normpath(os.path.join(config_folder, config_file_PK))

    PK = []
    with open(config_path_PK, "r") as f:
        for i in range(18):
            if i == 0:
                value = f.readline().replace('\n', '')
                PK.append(Element(pairing1, G1, value=value))
            elif i == 1:
                value = f.readline().replace('\n', '')
                PK.append(Element(pairing1, GT, value=value))
            else:
                value = f.readline().replace('\n', '')
                PK.append(Element(pairing1, G2, value=value))

    return params, MSK, PK



# 把Tree对象的树格式，生成列表，对应S参数
def collect_node_values(tree):
    values = []
    for node in tree.all_nodes_itr():
        values.append(str(node.tag))  # 使用 node.tag 来获取节点的值
    return values


# def collect_node_values(tree):
#     values = []
#     for node in tree.all_nodes_itr():
#         # 获取节点的子节点列表
#         children = tree.children(node.identifier)
#         # 如果子节点列表为空，则该节点为叶子节点
#         if not children:
#             values.append(str(node.tag))  # 这里只是示例如何判断，实际根据需要添加节点信息
#     return values



# 函数测试
if __name__ == '__main__':
    # a,b,c = IBBEKeyRead()
    # print(a)
    # print(b)
    # print(c)
    tree = gen_tree('b1090', 1, 10)
    print(tree)
    S = collect_node_values(tree)
    print(S)