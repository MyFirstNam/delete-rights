"""
此py文件定义安全协议解密类
类中包含的函数的具体功能：

"""

from time import sleep
from pypbc import *
import hashlib
import os
from treelib import Tree
from CenterSimulation.Model.SecurityProtocol.protocol_utils.busid_to_secret import busid_to_secret
from CenterSimulation.Model.SecurityProtocol.protocol_utils.hex_xor import hex_xor
from CenterSimulation.Model.SecurityProtocol.protocol_utils.sm3_hmac import hmac
from CenterSimulation.Model.SecurityProtocol.protocol_utils.pkcs5 import padPKCS7,unpadPKCS7
from CenterSimulation.Model.SecurityProtocol.protocol_utils.gen_tree import gen_tree
from json import dumps

from itertools import combinations
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from Crypto.Random import get_random_bytes

# 解密
class Decoder:
    def __init__(self):
        # self.pairing = None
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

    # 删除通知树解密
    def treeDecode(self,from_bus_id:str, to_bus_id:str, time_stamp:str, plaintext:str, segment_tree):
        """
        :param from_bus_id: 企业源头(当前节点的父节点)
        :param to_bus_id: 目标企业(当前节点)
        :param time_stamp: 时间戳
        :param plaintext: 数据内容
        :param segment_tree: 删除通知树
        上面是pkt的内容
        :return: next_bus_id_list:要传的企业list, next_segment_tree_list对接下来要发送的企业节点的Tree对象list
        """
        # 获取回话密钥
        secret_i = busid_to_secret(to_bus_id)
        key_i = hashlib.sha256((secret_i + time_stamp).encode()).hexdigest()  # 十六进制

        # 若为根节点
        if segment_tree.root == "root":
            pkt_mac_i = bytes.hex(hmac(bytes.fromhex(key_i), plaintext.encode()))

        else:
            pkt_mac_i = bytes.hex(hmac(bytes.fromhex(key_i), (plaintext + segment_tree.root).encode()))
        # 获取position位置的子节点SID
        sid_list = segment_tree.children(segment_tree.root)

        next_bus_id_list = []
        flag = 1
        for i in sid_list:
            last_bus_ip = bytes.hex(padPKCS7(from_bus_id.encode()))
            bus_ip = hex_xor(i.identifier, bytes.hex(
                hmac(bytes.fromhex(key_i), (last_bus_ip + pkt_mac_i + time_stamp + str(flag)).encode())))
            bus_id = unpadPKCS7(bytes.fromhex(bus_ip)).decode()

            next_bus_id_list.append(bus_id)
            flag = flag + 1
        # 路径验证
        for i in next_bus_id_list:
            if i == "center":
                break
            elif int(i[1:]) < 1000 or int(i[1:]) > 1099:
                return tuple(['NO1'])*4 # 下一条解密出错
            elif i == from_bus_id:
                return tuple(['NO2'])*4 # 路径重合出错
        # 修改segment_tree 对首结点mac后再发出子树
        next_segment_tree_list = []
        for i in sid_list:
            # 新建转发树
            tree = Tree()
            # 用这个包的to_bus_key对这一跳签名
            new_mac = bytes.hex(hmac(bytes.fromhex(key_i), bytes.fromhex(i.identifier)))
            tree.create_node(identifier=new_mac)
            # 获取子树children
            subtree = segment_tree.subtree(i.identifier)
            for j in subtree.children(subtree.get_node(i.identifier).identifier):
                origin_tree = segment_tree.subtree(j.identifier)
                # 复制
                tree.paste(new_mac, origin_tree)

            next_segment_tree_list.append(tree)

        return next_bus_id_list, next_segment_tree_list

    # ibbe解密
    def ibbeDecode(self,pub_param,payload:tuple):
        """
        pub_param：公共参数 类型：元组tuple
        payload:也是一个使用ibbeEncode加密产生的返回值 类型：元组tuple
        return:字符串明文 类型：str
        """
        if(self.params == None):
            print("未设置params，请设置后在使用当前方法！")
            return

        # 解密公共参数  S,SK,ID,PK 
        S,SK,ID,PK = pub_param

        # 解析payload  Hdry, iv, ciphertext（其实就是加密得到的结果）
        Hdry, iv, ciphertext = payload[0],payload[1],payload[2]
        
        # 解析公共参数
        
        # 对用户id排序后进行分组
        S.sort(reverse=False)
        S_list = [S[i:i + 15] for i in range(0, len(S), 15)]
        i = 0
        
        # 找出当前用户属于哪一个子list
        for i,S in enumerate(S_list):
            if ID in S:
                break
            
        # 找出那一组对应的解密参数
        S = S_list[i]
        Hdr,yi = Hdry[i]

        iv = bytes.fromhex(iv)
        iv1 = bytes.fromhex(ciphertext[0])

        ciphertext = bytes.fromhex(ciphertext[1])
        Ki = self.IBBE_Decrypt(S, SK,ID, Hdr, PK)
        t = Ki[0] + Ki[1]
        # 获得 32byte key
        Ki = bytes.fromhex('{:032x}'.format(t % (2 ** 128)))
        decipher = AES.new(Ki, AES.MODE_CBC, iv)
        key = decipher.decrypt(bytes.fromhex(yi))

        decipher = AES.new(key, AES.MODE_CBC, iv1)

        decrypted_padded_plaintext = decipher.decrypt(ciphertext)
        # 对解密后的明文进行去填充
        decrypted_plaintext = unpad(decrypted_padded_plaintext, AES.block_size)
        return decrypted_plaintext.decode()
        
        
   # 辅助ibbe解密
    def IBBE_Decrypt(self,S:list,SK,ID,Hdr,PK):
        """
        S, SK,ID, Hdr, PK
        进行具体的IBBE解密
        @param pairing: 双线性对 对象
        @param S: 含有参与加密的用户身份ID的list
        @param SK: 用户私钥
        @param ID: 用户身份ID
        @param Hdr: 含有[c1,c2]的list
        @param PK: 公钥
        @return: k 一个list
        """
        C1 = Hdr[0]
        C2 = Hdr[1]
        S_rm_val = [self.hash_Zr(i) for i in S if i!=ID]
        m = len(S_rm_val)
        h_ps = Element.one(self.pairing,G2)
        l = list(range(m))[::-1]
        dict_pre = {}
        dict_now = {}
        # count 用来统计循环数量
        count = 0
        for i in l:
            # count+=1
            # print(count)
            if m-1 == i:
                h_ps = Element(self.pairing, G2, value=h_ps*PK[i+2])
                continue
            if m-2 == i:
                c = list(combinations(range(m), m - i - 1))
                sum1 = Element.zero(self.pairing, Zr)
                for pair in c:
                    sum = Element.one(self.pairing, Zr)
                    for index in pair:
                        sum = sum.__mul__(S_rm_val[index])
                    sum1 = sum1.__add__(sum)
                    name = str(dumps(pair))
                    dict_now[name] = sum.__str__()
                h_ps = h_ps.__mul__(Element(self.pairing, G2, value=PK[i + 2] ** sum1))
                continue
            dict_pre = dict_now
            dict_now = {}
            c = list(combinations(range(m), m-i-1))
            sum1 = Element.zero(self.pairing,Zr)
            for pair in c:
                # count+=1
                # print(count)
                name = dumps(pair)
                pre_name = dumps(pair[:-1])
                sum = Element(self.pairing,Zr,value = int(dict_pre[pre_name][2:],16))
                sum = sum.__mul__(S_rm_val[pair[-1]])
                dict_now[name] = sum.__str__()
                sum1 = sum1.__add__(sum)
            h_ps = h_ps.__mul__(Element(self.pairing, G2, value=PK[i + 2]**sum1))
        t1 = self.pairing.apply(C1,h_ps)
        t2 = self.pairing.apply(SK,C2)
        t1t2 = Element(self.pairing,GT,value = t1*t2)

        s = Element.one(self.pairing, Zr)

        for i in S_rm_val:
            # count+=1
            # print(count)
            s = Element(self.pairing,Zr,s*i)

        s = s.__invert__()
        K = Element(self.pairing,GT,value=t1t2**s)

        return K

    def setup(self,qbits, rbits, m):
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

    def hash_Zr(self,ID):
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
    
    def Extract(self,MSK,ID):
        """
        生成用户私钥的方法
        @param pairing:双线性对 对象
        @param MSK: MSK主密钥
        @param ID: 用户身份
        @return:
        """
        t = Element(self.pairing, Zr, value=hash_Zr(ID) + MSK[1]).__invert__()
        SK = Element(self.pairing, G1, value=MSK[0] ** t)
        return SK

        """
        生成用户私钥的方法
        @param pairing:双线性对 对象
        @param MSK: MSK主密钥
        @param ID: 用户身份
        @return:
        """
        t = Element(pairing, Zr, value=hash_Zr(pairing, ID) + MSK[1]).__invert__()
        SK = Element(pairing, G1, value=MSK[0] ** t)
        return SK
    
# 测试样例
if __name__ == '__main__':
    #* 实例化对象
    decoder = Decoder()
    if True:
        # *测试treeDecode
        # 解密删除通知树
        from MessageEncoder import Encoder
        encoder = Encoder()
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
        treetest = gen_tree('b1000', 1, 10)
        print(treetest)
        segment_tree, SL = encoder.treeEncode(treetest,time_stamp,plaintext)

        def aaa(from_bus_id, to_bus_id, time_stamp, plaintext, segment_tree):
            print(from_bus_id + "--->" + to_bus_id)
            next_bus_ip_list, next_segment_tree_list = decoder.treeDecode(from_bus_id, to_bus_id, time_stamp,plaintext, segment_tree)
            for i, j in zip(next_bus_ip_list, next_segment_tree_list):
                if i == "center":
                    break
                else:
                    aaa(to_bus_id, i, time_stamp, plaintext, j)

        aaa('center', 'b1000',time_stamp, plaintext, segment_tree)

    # * 测试ibbeDecode

    if True:
        from MessageEncoder import Encoder
        encoder = Encoder()
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
        for i in range(5):
            S.append('b' + str(1000+i))
        payload = encoder.ibbeEncode((S,PK,MSK),plaintext)


        decoder.setParams(params.__str__())
        # 进行解密操作
        ID = "b1000"
        SK = encoder.Extract(MSK,ID)
        pub_param = (S,SK,ID,PK)
        try:
            newPlaintext = decoder.ibbeDecode(pub_param,payload)
            print(newPlaintext)
        except Exception as e:
            print(e)


