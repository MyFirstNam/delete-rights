from treelib import Tree,Node
class PathSelect:
    def __init__(self, pathtree: dict):
        self.tree_data = pathtree

    # 根据当前节点，得到后续节点

    def find_node_and_children(self, target_node_key):
        return self._find_node_and_children(self.tree_data, target_node_key)

    def _find_node_and_children(self, tree, target_node_key):
        if target_node_key in tree:
            return tree[target_node_key]
        for node_key, children in tree.items():
            if isinstance(children, list):
                for child in children:
                    result = self._find_node_and_children(child, target_node_key)
                    if result:
                        return result
        return None

class TreeParentFinder:
    def __init__(self, tree):
        self.tree = tree

    # 根据当前节点，得到父节点

    def find_parent(self, target_node_key, current_tree=None, parent_key=None):
        if current_tree is None:
            current_tree = self.tree

        if target_node_key in current_tree:
            return parent_key

        for key, value in current_tree.items():
            if isinstance(value, list):
                for subtree in value:
                    result = self.find_parent(target_node_key, subtree, key)
                    if result:
                        return result
        return None

# 示例数据
# deleteNotifytree = {
#     "b1000": [
#         {"b1001": [
#             {"b1002": []}
#         ]},
#         {"b1003": [
#             {"b1004": []}
#         ]}
#     ]
# }

#
# # # # 查找节点 "b1001" 及其子节点
# target_node_key = "b1004"
# test = TreeParentFinder(deleteNotifytree)
# result = test.find_parent(target_node_key)
# if result:
#     print(f"节点 {target_node_key} 及其父节点: {result}")
# else:
#     print(f"未找到节点 {target_node_key}")
#
# getnextNode = PathSelect(deleteNotifytree)
# nextnode = getnextNode.find_node_and_children("b1000")
# keys_list = []
# for dictionary in nextnode:  # 字符串转换
#     for key in dictionary.keys():
#         keys_list.append(key)
#
# print(keys_list)
# print(nextnode)