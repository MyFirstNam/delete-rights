"""
函数说明：
    辅助返回一个树中的所有节点值和其位置，返回两个列表
"""


def delNotifyAckVerify(tree):
    """
    按层次和位置从左向右遍历 treelib 中的节点
    :param tree: treelib.Tree 实例
    :return: 节点的 tag 组成的列表，按照从左到右的顺序排列
    """
    result = []  # 用于存储遍历结果的列表
    pos_list = []
    q = [(tree.get_node(tree.root), 1)]  # 初始化队列，包含根节点、层次
    # 遍历队列，直到队列为空
    layer_num = 1
    current_layer = 1
    while len(q) > 0:
        node, layer = q.pop(0)  # 取出队首节点
        # 将当前节点的 tag 加入结果列表中
        if node.identifier is not None:
            if layer != current_layer:
                current_layer += 1
            layer_num = 1
            result.append(node.identifier)
            pos_list.append((current_layer, layer_num))
            layer_num += 1
        if node.is_leaf():  # 如果当前节点是叶节点，继续遍历下一个节点
            continue
        # 获取当前节点的子节点
        children = tree.children(node.identifier)
        # 将子节点加入队列中待访问，并记录它们的层次和位置信息
        for i, child in enumerate(children):
            q.append((child, layer + 1))
        # 返回遍历结果
        # global_logger.info(f"result:{result}")
        # global_logger.info(f"pos_list:{pos_list}")

    return result, pos_list


# node_set = set(delNotifyAckVerify(SL)[0])  # SL就是 treeEncode 返回的删除确认树
# for key in dict_ack:
#     if (dict_ack[key] not in node_set):
#         print(key.split("-")[0], "的删除凭证验证出错")
