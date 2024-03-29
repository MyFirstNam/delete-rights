# from Simulation.exts import global_logger
def get_node_position(tree, element):
    """
    :param tree: 输入的treelib
    :param element: 树的元素
    :return: 树在元素中的位置 根节点为(0,0) 第一个参数表示深度 第二个表示对应深度子位置 从左到右
    """
    node_id = tree.get_node(element).identifier
    # 获取node
    node = tree.get_node(node_id)
    if node.is_root():
        return (0, 0)
    # 父亲节点
    parent = tree.parent(node.identifier)
    # 兄弟节点
    siblings = tree.children(parent.identifier)
    if node not in siblings:
        print(f"Error: node {node_id} not in siblings {siblings}")
        return None
    index = siblings.index(node)
    parent_position = get_node_position(tree, parent.identifier)
    depth = parent_position[0] + 1
    raw_position = (depth, index)
    return raw_position


def get_node_position2(tree, element):
    """
    获取真实位置
    :param tree:
    :param element:
    :return:
    """
    depth = tree.depth(element) + 1
    num = 1
    for bus_id in traverse(tree)[0]:
        if bus_id == element:
            break
        if tree.depth(bus_id) + 1 == depth:
            num += 1
    return depth, num


def traverse(tree):

    """
    按层次和位置从左向右遍历 treelib 中的节点
    :param tree: treelib.Tree 实例
    :return: 节点的 tag 组成的列表，按照从左到右的顺序排列
    """
    result = []  # 用于存储遍历结果的列表
    pos_list = []
    q = [(tree.get_node(tree.root),1)]  # 初始化队列，包含根节点、层次
    # 遍历队列，直到队列为空
    layer_num = 1
    current_layer = 1
    while len(q) > 0:
        node,layer = q.pop(0)  # 取出队首节点
        # 将当前节点的 tag 加入结果列表中
        if node.identifier is not None:
            if layer != current_layer:
                current_layer += 1
                layer_num = 1
            result.append(node.identifier)
            pos_list.append((current_layer,layer_num))
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
    return result,pos_list


def get_position_node(tree, position):
    traverse_elements = traverse(tree)[0]
    for i in traverse_elements:
        i_position = get_node_position2(tree, i)
        if i_position == position:
            return i
