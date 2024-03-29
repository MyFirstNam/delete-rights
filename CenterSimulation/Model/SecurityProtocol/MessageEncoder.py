"""
此py文件定义安全协议解密类
类中包含的函数的具体功能：

"""
from time import sleep
from pypbc import *
import hashlib
import os
from treelib import Tree, Node
from CenterSimulation.Model.SecurityProtocol.protocol_utils.busid_to_secret import busid_to_secret
from CenterSimulation.Model.SecurityProtocol.protocol_utils.busid_to_secret import busid_to_IBBE_secret
from CenterSimulation.Model.SecurityProtocol.protocol_utils.hex_xor import hex_xor
from CenterSimulation.Model.SecurityProtocol.protocol_utils.sm3_hmac import hmac
from CenterSimulation.Model.SecurityProtocol.protocol_utils.tree_pos import traverse
from CenterSimulation.Model.SecurityProtocol.protocol_utils.pkcs5 import padPKCS7
from CenterSimulation.Model.SecurityProtocol.protocol_utils.gen_tree import gen_tree
from json import dumps

from itertools import combinations
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes


# 加密
class Encoder:
    def __init__(self):
        self.pairing = None
        self.params = None

    def setParams(self, params: str):
        """
        为对象设置str类型的Params，params是形成双线性对的基本参数，有了它就确定了双线性对
        @param params: str类型的Params
        @return:
        """
        self.params = Parameters(params)
        self.pairing = Pairing(self.params)

    # 删除通知树加密（生成删除通知树）
    def treeEncode(self, delete_tree: Tree, time_stamp: str, plaintext: str):
        """
        用于对数据流转树进行处理得到删除通知树
        :param delete_tree: 数据流转树
        :param time_stamp: 时间戳
        :param plaintext: 明文信息
        :return: Segment_Tree->用于删除通知传播 (删除通知树)，SL签名树-> 用于中心监管机构最终检验正确性(删除确认树)
        """

        SL = Tree()
        SL.create_node(identifier='root')
        segment_tree = Tree()
        segment_tree.create_node(identifier='root')

        # 给delete树增加一层节点，对应安全协议中初始化，增加一层节点
        for i, leave in enumerate(delete_tree.leaves()):
            delete_tree.create_node(identifier='leave' + str(i), parent=leave.identifier)

        # 将根节点存储在对应的列表中
        SL_que = [SL.get_node(SL.root)]
        # todo 下面这行是不是写错了，应该是segment_tree
        sg_que = [segment_tree.get_node(SL.root)]

        # 层序遍历
        for bus_id, position in zip(*traverse(delete_tree)):
            if delete_tree.get_node(bus_id).is_leaf():
                # 判断当前节点是否是叶子节点，如果是叶子节点，两个列表各弹出一个元素，然后继续进行下一次循环
                SL_que.pop(0)
                sg_que.pop(0)
                continue
            # 这一行是查找对应bus_id的密钥，这个函数的内容是查找密钥
            secret = busid_to_secret(bus_id)
            # 计算生成会话密钥
            key = hashlib.sha256((secret + time_stamp).encode()).hexdigest()  # 输出十六进制session key

            # position = get_node_position2(delete_tree, bus_id)  # 获取 在delete中的位置
            # print(position)
            # 找到处于deletetree 中该节点 children
            parent_id = None
            # 如果父节点不为空
            if delete_tree.parent(bus_id):
                parent_id = delete_tree.parent(bus_id).identifier  # 根节点的parent_id 为None

            children_id = [i.identifier for i in delete_tree.children(bus_id)]
            cur_SL = SL_que.pop(0)
            cur_sg = sg_que.pop(0)
            for i, child_id in enumerate(children_id):

                if position[0] == 1 and position[1] == 1:  # 若为根节点
                    pktMAC = bytes.hex(hmac(key=bytes.fromhex(key), msg=plaintext.encode()))  # 十六进制

                    IP_last = bytes.hex(padPKCS7(b'center'))  # 十六进制

                    if child_id[0] != 'l':
                        IP_next = bytes.hex(padPKCS7(child_id.encode()))  # 十六进制

                    else:
                        IP_next = bytes.hex(padPKCS7(b'center'))

                    SID = hex_xor(IP_next, bytes.hex(
                        hmac(bytes.fromhex(key), (IP_last + pktMAC + time_stamp + str(i + 1)).encode())))
                else:
                    # todo 可能会错误,get_position_node
                    msg = plaintext + cur_SL.identifier
                    pktMAC = bytes.hex(hmac(key=bytes.fromhex(key), msg=msg.encode()))

                    IP_last = bytes.hex(padPKCS7(parent_id.encode()))  # 十六进制

                    if child_id[0] != 'l':
                        IP_next = bytes.hex(padPKCS7(child_id.encode()))  # 十六进制

                    else:
                        IP_next = bytes.hex(padPKCS7(b'center'))

                    SID = hex_xor(IP_next, bytes.hex(
                        hmac(bytes.fromhex(key), (IP_last + pktMAC + time_stamp + str(i + 1)).encode())))
                segment_tree.create_node(identifier=SID, parent=cur_sg)
                iden_sl = bytes.hex(hmac(bytes.fromhex(key), bytes.fromhex(SID)))
                SL.create_node(identifier=iden_sl,
                               parent=cur_SL)
                # 队列添加代码
                sg_que.append(segment_tree.get_node(SID))
                SL_que.append(SL.get_node(iden_sl))
        return segment_tree, SL

    # ibbe加密
    def ibbeEncode(self, pub_param, plaintext):
        # 解析公共参数 pub_param S,PK,MSK
        S, PK, MSK = pub_param
        if (self.params == None):
            print("未设置params，请设置后在使用当前方法！")
            return
        S.sort(reverse=False)

        # 对用户id排序后进行分组
        S_list = [S[i:i + 15] for i in range(0, len(S), 15)]

        # 生成随机密钥
        key = bytes.hex(get_random_bytes(32))
        Hdry = []

        # 生成随机iv，目的是加密上面生成的随机值key，从而得到yi，yi为后续解密出key使用
        iv = get_random_bytes(AES.block_size)

        # 为每一分组生成 yi以及hdri
        for S in S_list:
            Hdri, Ki = self.IBBE_Encrypt(S, PK, MSK)
            t = Ki[0] + Ki[1]
            # 获得 32byte key
            Ki = bytes.fromhex('{:032x}'.format(t % 2 ** 128))
            # 生成随机的初始向量
            cipher = AES.new(Ki, AES.MODE_CBC, iv)
            yi = bytes.hex(cipher.encrypt(bytes.fromhex(key)))
            Hdry.append((Hdri, yi))

        # 使用key对明文进行AES加密
        plaintext = plaintext.encode()
        iv1 = get_random_bytes(AES.block_size)
        padded_plaintext = pad(plaintext, AES.block_size)
        cipher = AES.new(bytes.fromhex(key), AES.MODE_CBC, iv1)
        ciphertext = cipher.encrypt(padded_plaintext)

        # 序列化 Hdry

        for i, (Hdr, y) in enumerate(Hdry):
            Hdr = [i.__str__() for i in Hdr]
            Hdry[i] = (Hdr, y)
        # Hdry = json.dumps(Hdry)

        return (Hdry, bytes.hex(iv), (bytes.hex(iv1), bytes.hex(ciphertext)))

    # 辅助ibbe加密
    def IBBE_Encrypt(self, S: list, PK, MSK: list):
        """
        进行具体的加密
        @param S: 含有参与加密的用户身份ID的list
        @param PK:公钥
        @param MSK:主密钥
        @return: k一个list
        """
        k = Element.random(self.pairing, Zr)
        C1 = Element(self.pairing, G1, value=PK[0] ** (k.__neg__()))
        t = k
        for ID in S:
            t = Element(self.pairing, Zr, value=t * (MSK[1] + self.hash_Zr(ID)))
        C2 = Element(self.pairing, G2, value=PK[2] ** (t))
        K = Element(self.pairing, GT, value=PK[1] ** k)
        Hdr = [C1, C2]
        return Hdr, K

    def setup(self, qbits, rbits, m):
        """
        初始化算法参数
        @param qbits:
        @param rbits:
        @param m:
        @return: 返回所需要的MSK以及PK
        """
        # 生成双线对参数
        params = Parameters(qbits=qbits, rbits=rbits)

        # 根据参数实例化双线性 对返回公共参数，PEKS是对称双线性对，G1=G2,二者的生成元是一样的，G2同样可以替换为G1
        # 根据参数实例化双线性对
        pairing = Pairing(params)

        # g是G2的一个生成元
        g = Element.random(pairing, G1)  # g是G2的一个生成元
        h = Element.random(pairing, G2)

        # MSK=【g，gama】
        gama = Element.random(pairing, Zr)
        MSK = [g, gama]

        # 公钥是[w=g^gama, v = g*h...]
        PK = []
        w = Element(pairing, G1, value=g ** gama)
        v = pairing.apply(g, h)
        PK.append(w)
        PK.append(v)

        # 生成公钥剩余部分
        for i in range(m + 1):
            t = Element(pairing, G2, value=h ** (gama ** i))
            PK.append(t)
        return params, MSK, PK

    def hash_Zr(self, ID):
        '''
        hash操作,并将结果映射到Zr上
        @param ID:用户身份
        @return: 映射值
        '''
        hash_obj = hashlib.sha256(ID.encode())
        hash_str = hash_obj.digest()
        # 将二进制字符串转换为整数
        h = int.from_bytes(hash_str, byteorder='big')
        # 取模得到 Zp 中的值
        return Element(self.pairing, Zr, value=h)

    def Extract(self, MSK, ID):
        """
        生成用户私钥的方法
        @param pairing:双线性对 对象
        @param MSK: MSK主密钥
        @param ID: 用户身份
        @return:
        """
        t = Element(self.pairing, Zr, value=self.hash_Zr(ID) + MSK[1]).__invert__()
        SK = Element(self.pairing, G1, value=MSK[0] ** t)
        return SK


# 测试样例
if __name__ == '__main__':
    # * 实例化对象
    encoder = Encoder()

    # *测试treeEncode
    if True:
        user_id = 'u100000000'
        info_id = 'i1'
        row_business_id = 'b1000'
        res = []
        data = {
            'user_id': user_id,
            'info_id': info_id,
            'row_business_id': row_business_id
        }
        plaintext = dumps(data)
        time_stamp = "1700386032.2781575"
        treetest = gen_tree('b1090', 1, 10)
        l1, l2 = encoder.treeEncode(treetest, time_stamp, plaintext)
        print(l1)
        print(l2)


    # * 测试 ibbeEncode
    from MessageDecoder import Decoder

    if True:
        user_id = 'u100000000'
        info_id = 'i1'
        row_business_id = 'b1000'
        data = {
            'user_id': user_id,
            'info_id': info_id,
            'row_business_id': row_business_id
        }
        plaintext = dumps(data)

        # params, MSK, PK = encoder.setup(qbits=512, rbits=160, m=15)

        # 获取当前文件的绝对路径
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # 设置相对于当前文件的路径
        config_folder = os.path.join(current_dir, '../../', 'Resource/IBBE_params')
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



        encoder.setParams(params.__str__())
        # 生成S参数
        S = []
        for i in range(15):
            S.append('b' + str(1000 + i))
        print(S)
        payload = encoder.ibbeEncode((S, PK, MSK), plaintext)
        print(payload)


        # 进行解密操作
        decoder = Decoder()
        decoder.setParams(params.__str__())
        ID = 'b1000'
        # SK = encoder.Extract(MSK,ID)
        # print(SK)
        # print(type(SK))
        # 用于保存生成100个密钥
        # config_file_sk = 'IBBE_secret_key.txt'
        # # 组合并规范化路径
        # config_path_sk = os.path.normpath(os.path.join(config_folder, config_file_sk))
        #
        # with open(config_path_sk, 'w') as f:
        #     for i in range(100):
        #         ID = 'b' + str((1000 + i))
        #         SK = encoder.Extract(MSK, ID)
        #         s = SK.__str__()
        #         f.write(s + '\n')

        # def bus_to_IBBE_secret(busid):
        #     config_file_sk = 'IBBE_secret_key.txt'
        #     # 组合并规范化路径
        #     config_path_sk = os.path.normpath(os.path.join(config_folder, config_file_sk))
        #     line_index = int(busid[2:]) + 1
        #     with open(config_path_sk, 'r') as f:
        #         for i in range(line_index):
        #             line = f.readline()
        #     return line.replace('\n', '')

        SK = Element(pairing1, G2, busid_to_IBBE_secret(ID))

        pub_param = (S, SK, ID, PK)
        try:
            newPlaintext = decoder.ibbeDecode(pub_param, payload)
            print(newPlaintext)
        except Exception as e:
            print(e)
