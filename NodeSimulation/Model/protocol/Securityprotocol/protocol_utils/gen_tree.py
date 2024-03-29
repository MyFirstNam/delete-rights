from treelib import Tree,Node
#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：Del_Notify 
@File    ：gen_tree.py.py
@IDE     ：PyCharm 
@Author  ：小豪
@Date    ：2023/10/22 13:41 
'''

def gen_tree(row_business_id:str,type:int, num:int):
    """

    @param row_business_id:树根节点
    @param type:树的种类，0表示广度，1表示深度
    @param num: 树的规模，即树上有多少节点
    @return: 统一表示为以b1000为根节点的树
    """
    tree = Tree()
    tree.create_node(identifier=row_business_id)  # 根节点
    base = int(row_business_id[2:])
    if(type == 0):
        for i in range(num-1):
            tree.create_node(identifier='b'+str(1000+(i+1+base)%100), parent=row_business_id)
    else:
        for i in range(num-1):
            tree.create_node(identifier='b'+str(1000+(i+1+base)%100), parent='b'+str(1000+(i+base)%100))
    return tree


if __name__ == '__main__':
    d = (1,2,3)
    a,b,c = d
    print(a,b,c)
    tree = gen_tree("b1000",1,5)
    print(tree)
