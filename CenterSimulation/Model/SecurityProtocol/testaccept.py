import sys
sys.path.append('/home/dengx/deng_delete2_6/')

from flask import Flask, request, jsonify, Blueprint
import json
from CenterSimulation.Utils.IBBEKeyRead import IBBEKeyRead, collect_node_values
from CenterSimulation.Model.SecurityProtocol import MessageEncoder
from CenterSimulation.Model.SecurityProtocol.protocol_utils.busid_to_secret import busid_to_IBBE_secret
from entry import ibbeDecode
import requests
from pypbc import *
import hashlib
from json import dumps
from itertools import combinations
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad, pad
from Crypto.Random import get_random_bytes

# 解密


# ibbe解密
# def ibbeDecode(params, pairing, pub_param, payload: tuple):
#     """
#     pub_param：公共参数 类型：元组tuple
#     payload:也是一个使用ibbeEncode加密产生的返回值 类型：元组tuple
#     return:字符串明文 类型：str
#     """
#     if (params == None):
#         print("未设置params，请设置后在使用当前方法！")
#         return
#
#     # 解密公共参数  S,SK,ID,PK
#     S, SK, ID, PK = pub_param
#
#     # 解析payload  Hdry, iv, ciphertext（其实就是加密得到的结果）
#     Hdry, iv, ciphertext = payload[0], payload[1], payload[2]
#
#     # 解析公共参数
#
#     # 对用户id排序后进行分组
#     S.sort(reverse=False)
#     S_list = [S[i:i + 15] for i in range(0, len(S), 15)]
#     i = 0
#
#     # 找出当前用户属于哪一个子list
#     for i, S in enumerate(S_list):
#         if ID in S:
#             break
#
#     # 找出那一组对应的解密参数
#     S = S_list[i]
#     Hdr, yi = Hdry[i]
#
#     iv = bytes.fromhex(iv)
#     iv1 = bytes.fromhex(ciphertext[0])
#
#     ciphertext = bytes.fromhex(ciphertext[1])
#     Ki = IBBE_Decrypt(pairing, S, SK, ID, Hdr, PK)
#     t = Ki[0] + Ki[1]
#     # 获得 32byte key
#     Ki = bytes.fromhex('{:032x}'.format(t % (2 ** 128)))
#     decipher = AES.new(Ki, AES.MODE_CBC, iv)
#     key = decipher.decrypt(bytes.fromhex(yi))
#
#     decipher = AES.new(key, AES.MODE_CBC, iv1)
#
#     decrypted_padded_plaintext = decipher.decrypt(ciphertext)
#     # 对解密后的明文进行去填充
#     decrypted_plaintext = unpad(decrypted_padded_plaintext, AES.block_size)
#     return decrypted_plaintext.decode()
#
#
# # 辅助ibbe解密
# def IBBE_Decrypt(pairing, S: list, SK, ID, Hdr, PK):
#     """
#     S, SK,ID, Hdr, PK
#     进行具体的IBBE解密
#     @param pairing: 双线性对 对象
#     @param S: 含有参与加密的用户身份ID的list
#     @param SK: 用户私钥
#     @param ID: 用户身份ID
#     @param Hdr: 含有[c1,c2]的list
#     @param PK: 公钥
#     @return: k 一个list
#     """
#     C1 = Hdr[0]
#     C2 = Hdr[1]
#     S_rm_val = [hash_Zr(pairing, i) for i in S if i != ID]
#     m = len(S_rm_val)
#     h_ps = Element.one(pairing, G2)
#     l = list(range(m))[::-1]
#     dict_pre = {}
#     dict_now = {}
#     # count 用来统计循环数量
#     count = 0
#     for i in l:
#         # count+=1
#         # print(count)
#         if m - 1 == i:
#             h_ps = Element(pairing, G2, value=h_ps * PK[i + 2])
#             continue
#         if m - 2 == i:
#             c = list(combinations(range(m), m - i - 1))
#             sum1 = Element.zero(pairing, Zr)
#             for pair in c:
#                 sum = Element.one(pairing, Zr)
#                 for index in pair:
#                     sum = sum.__mul__(S_rm_val[index])
#                 sum1 = sum1.__add__(sum)
#                 name = str(dumps(pair))
#                 dict_now[name] = sum.__str__()
#             h_ps = h_ps.__mul__(Element(pairing, G2, value=PK[i + 2] ** sum1))
#             continue
#         dict_pre = dict_now
#         dict_now = {}
#         c = list(combinations(range(m), m - i - 1))
#         sum1 = Element.zero(pairing, Zr)
#         for pair in c:
#             # count+=1
#             # print(count)
#             name = dumps(pair)
#             pre_name = dumps(pair[:-1])
#             sum = Element(pairing, Zr, value=int(dict_pre[pre_name][2:], 16))
#             sum = sum.__mul__(S_rm_val[pair[-1]])
#             dict_now[name] = sum.__str__()
#             sum1 = sum1.__add__(sum)
#         h_ps = h_ps.__mul__(Element(pairing, G2, value=PK[i + 2] ** sum1))
#     t1 = pairing.apply(C1, h_ps)
#     t2 = pairing.apply(SK, C2)
#     t1t2 = Element(pairing, GT, value=t1 * t2)
#
#     s = Element.one(pairing, Zr)
#
#     for i in S_rm_val:
#         # count+=1
#         # print(count)
#         s = Element(pairing, Zr, s * i)
#
#     s = s.__invert__()
#     K = Element(pairing, GT, value=t1t2 ** s)
#
#     return K
#
# def hash_Zr(pairing, ID):
#     '''
#     hash操作,并将结果映射到Zr上
#     @param ID:用户身份
#     @return: 映射值
#     '''
#     hash_obj = hashlib.sha256(ID.encode())
#     hash_str = hash_obj.digest()
#     # 将二进制字符串转换为整数
#     h = int.from_bytes(hash_str, byteorder='big')
#     # 取模得到 Zp 中的值
#     return Element(pairing, Zr, value=h)
#
#
#
#



# def setup(qbits, rbits, m):
#     """
#     初始化算法参数
#     @param qbits:
#     @param rbits:
#     @param m:
#     @return: 返回所需要的MSK以及PK
#     """
#     # 生成双线对参数
#     params = Parameters(qbits=qbits, rbits=rbits)
#
#     # 根据参数实例化双线性 对返回公共参数，PEKS是对称双线性对，G1=G2,二者的生成元是一样的，G2同样可以替换为G1
#     # 根据参数实例化双线性对
#     pairing = Pairing(params)
#
#     # g是G2的一个生成元
#     g = Element.random(pairing, G1)  # g是G2的一个生成元
#     h = Element.random(pairing, G2)
#
#     # MSK=【g，gama】
#     gama = Element.random(pairing, Zr)
#     MSK = [g, gama]
#
#     # 公钥是[w=g^gama, v = g*h...]
#     PK = []
#     w = Element(pairing, G1, value=g ** gama)
#     v = pairing.apply(g, h)
#     PK.append(w)
#     PK.append(v)
#
#     # 生成公钥剩余部分
#     for i in range(m + 1):
#         t = Element(pairing, G2, value=h ** (gama ** i))
#         PK.append(t)
#     return params, MSK, PK
#
#
# def hash_Zr(pairing, ID):
#     '''
#     hash操作，并将结果映射到Zr上
#     @param ID:用户身份
#     @return: 映射值
#     '''
#     hash_obj = hashlib.sha256(ID.encode())
#     hash_str = hash_obj.digest()
#     # 将二进制字符串转换为整数
#     h = int.from_bytes(hash_str, byteorder='big')
#     # 取模得到 Zp 中的值
#     return Element(pairing, Zr, value=h)
#
#
# def Extract(pairing, MSK, ID):
#     """
#     生成用户私钥的方法
#     @param pairing:双线性对 对象
#     @param MSK: MSK主密钥
#     @param ID: 用户身份
#     @return:
#     """
#     t = Element(pairing, Zr, value=hash_Zr(pairing, ID) + MSK[1]).__invert__()
#     SK = Element(pairing, G1, value=MSK[0] ** t)
#     return SK
#
#
# def IBBE_Encrypt(pairing, S: list, PK, MSK: list):
#     """
#     进行具体的加密
#     @param pairing:双线性对 对象
#     @param S: 含有参与加密的用户身份ID的list
#     @param PK:公钥
#     @param MSK:主密钥
#     @return: k一个list
#     """
#     k = Element.random(pairing, Zr)
#     C1 = Element(pairing, G1, value=PK[0] ** (k.__neg__()))
#     t = k
#     for ID in S:
#         t = Element(pairing, Zr, value=t * (MSK[1] + hash_Zr(pairing, ID)))
#     C2 = Element(pairing, G2, value=PK[2] ** (t))
#     K = Element(pairing, GT, value=PK[1] ** k)
#     Hdr = [C1, C2]
#     return Hdr, K
#
#
# def IBBE_Decrypt(pairing, S: list, SK, ID, Hdr, PK):
#     """
#     进行具体的IBBE解密
#     @param pairing: 双线性对 对象
#     @param S: 含有参与加密的用户身份ID的list
#     @param SK: 用户私钥
#     @param ID: 用户身份ID
#     @param Hdr: 含有[c1,c2]的list
#     @param PK: 公钥
#     @return: k 一个list
#     """
#     C1 = Hdr[0]
#     C2 = Hdr[1]
#     S_rm_val = [hash_Zr(pairing, i) for i in S if i != ID]
#     m = len(S_rm_val)
#     h_ps = Element.one(pairing, G2)
#     l = list(range(m))[::-1]
#     dict_pre = {}
#     dict_now = {}
#     for i in l:
#         if m - 1 == i:
#             h_ps = Element(pairing, G2, value=h_ps * PK[i + 2])
#             continue
#         if m - 2 == i:
#             c = list(combinations(range(m), m - i - 1))
#             sum1 = Element.zero(pairing, Zr)
#             for pair in c:
#                 sum = Element.one(pairing, Zr)
#                 for index in pair:
#                     sum = sum.__mul__(S_rm_val[index])
#                 sum1 = sum1.__add__(sum)
#                 name = str(json.dumps(pair))
#                 dict_now[name] = sum.__str__()
#             h_ps = h_ps.__mul__(Element(pairing, G2, value=PK[i + 2] ** sum1))
#             continue
#         dict_pre = dict_now
#         dict_now = {}
#         c = list(combinations(range(m), m - i - 1))
#         sum1 = Element.zero(pairing, Zr)
#         for pair in c:
#             name = json.dumps(pair)
#             pre_name = json.dumps(pair[:-1])
#             sum = Element(pairing, Zr, value=int(dict_pre[pre_name][2:], 16))
#             sum = sum.__mul__(S_rm_val[pair[-1]])
#             dict_now[name] = sum.__str__()
#             sum1 = sum1.__add__(sum)
#         h_ps = h_ps.__mul__(Element(pairing, G2, value=PK[i + 2] ** sum1))
#
#     t1 = pairing.apply(C1, h_ps)
#     t2 = pairing.apply(SK, C2)
#     t1t2 = Element(pairing, GT, value=t1 * t2)
#
#     s = Element.one(pairing, Zr)
#
#     for i in S_rm_val:
#         s = Element(pairing, Zr, s * i)
#
#     s = s.__invert__()
#     K = Element(pairing, GT, value=t1t2 ** s)
#
#     return K
#
#
# def Encrypt(pairing, S, PK, MSK: list, plaintext):
#     """
#     进一步使用IBBE生成的密钥k，使用k进一步生成用于加密密文的对称密钥key，
#     具体使用的加密方法为 AES
#     @param pairing:双线性对 对象
#     @param S:含有参与加密的用户身份ID的list
#     @param PK: 公钥
#     @param MSK: 主密钥
#     @param plaintext: 明文
#     @return:用于解密K的Hdr以及用于使用key解密出明文的iv以及密文
#     """
#     S.sort(reverse=False)
#     S_list = [S[i:i + 15] for i in range(0, len(S), 15)]
#     key = bytes.hex(get_random_bytes(32))
#     Hdry = []
#     iv = get_random_bytes(AES.block_size)
#     for S in S_list:
#         Hdri, Ki = IBBE_Encrypt(pairing, S, PK, MSK)
#         t = Ki[0] + Ki[1]
#         # 获得 32byte key
#         Ki = bytes.fromhex('{:032x}'.format(t % 2 ** 128))
#         # 生成随机的初始向量
#         cipher = AES.new(Ki, AES.MODE_CBC, iv)
#         yi = bytes.hex(cipher.encrypt(bytes.fromhex(key)))
#         Hdry.append((Hdri, yi))
#     plaintext = plaintext.encode()
#     iv1 = get_random_bytes(AES.block_size)
#     padded_plaintext = pad(plaintext, AES.block_size)
#     cipher = AES.new(bytes.fromhex(key), AES.MODE_CBC, iv1)
#     ciphertext = cipher.encrypt(padded_plaintext)
#     return Hdry, bytes.hex(iv), ((bytes.hex(iv1), bytes.hex(ciphertext)))
#
#
# def Decrypt(pairing, S: list, SK, ID, Hdry, PK, iv, ciphertext):
#     """
#     IBBE分组加密
#     @param pairing:
#     @param S:
#     @param SK:
#     @param ID:
#     @param Hdry:
#     @param PK:
#     @param iv:
#     @param ciphertext:
#     @return:
#     """
#     S.sort(reverse=False)
#     S_list = [S[i:i + 15] for i in range(0, len(S), 15)]
#     i = 0
#     for i, S in enumerate(S_list):
#         if ID in S:
#             break
#     S = S_list[i]
#     Hdr, yi = Hdry[i]
#
#     iv = bytes.fromhex(iv)
#     iv1 = bytes.fromhex(ciphertext[0])
#
#     ciphertext = bytes.fromhex(ciphertext[1])
#     Ki = IBBE_Decrypt(pairing, S, SK, ID, Hdr, PK)
#     t = Ki[0] + Ki[1]
#     # 获得 32byte key
#     Ki = bytes.fromhex('{:032x}'.format(t % 2 ** 128))
#     decipher = AES.new(Ki, AES.MODE_CBC, iv)
#     key = decipher.decrypt(bytes.fromhex(yi))
#
#     decipher = AES.new(key, AES.MODE_CBC, iv1)
#
#     decrypted_padded_plaintext = decipher.decrypt(ciphertext)
#     # 对解密后的明文进行去填充
#     decrypted_plaintext = unpad(decrypted_padded_plaintext, AES.block_size)
#     return decrypted_plaintext.decode()
#
#
# from flask import Flask
#
# app = Flask(__name__)
#
#
# @app.route('/hello', methods=['GET'])
# def hello():
#     # params, MSK, PK = setup(qbits=512, rbits=160, m=30)
#     params, MSK, PK = IBBEKeyRead()
#     pairing = Pairing(params)
#     # SK_0 = Extract(pairing, MSK, 'b1000')
#     # 测试从1到25开始测试
#     time_list = []
#     # for i in range(1, 10):
#     #     S = []
#     #     for j in range(i):
#     #         name = 'b' + str(1000 + j)
#     #         S.append(name)
#     S = ['b1000', 'b1001', 'b1002']
#     plaintext = 'hello world'
#     ID = 'b1000'
#     # * 实例化对象
#     encoder = MessageEncoder.Encoder()
#     encoder.setParams(params.__str__())
#
#     # IBBE加密
#     plaintext = dumps(plaintext)
#
#     # payload = encoder.ibbeEncode((S, PK, MSK), plaintext)
#     Hdry, iv, ciphertext = Encrypt(pairing, S, PK, MSK, plaintext)
#     print("payload加密内容如下:")
#     print(ciphertext)
#     # print(payload)
#
#     # # 解析payload  Hdry, iv, ciphertext（其实就是加密得到的结果）
#     # # Hdry, iv, ciphertext = payload[0], payload[1], payload[2]
#     SK_0 = Element(pairing, G2, busid_to_IBBE_secret(ID))
#     # # SK_0 = Extract(pairing, MSK, 'b1000')
#     # # new_plaintext = Decrypt(pairing, S, SK_0, ID, Hdry, PK, iv, ciphertext)
#     #
#     pub_param = (S, SK_0, ID, PK)
#     payload = (Hdry, bytes.hex(iv), ((bytes.hex(iv), bytes.hex(ciphertext))))
#     try:
#         newPlaintext = ibbeDecode(params, pairing, pub_param, payload)
#         print(newPlaintext)
#     except Exception as e:
#         print(e)
#
#     return "Yes"
#
# if __name__ == '__main__':
#     app.run(debug=True, port=5000, host="127.0.0.1")

import jsonpickle

testacc = Flask(__name__)
@testacc.route("/tree/postx/endpointx", methods=['POST'])
# POST格式为JSON格式
def testaccpt():
    data = request.json
    data = json.loads(data)
    print(data)

    # 调用辅助函数读取IBBE加密需要的 params, MSK, PK参数
    params, MSK, PK = IBBEKeyRead()

    # * 实例化对象
    encoder = MessageEncoder.Encoder()
    encoder.setParams(params.__str__())

    # 生成S参数 S参数是一个列表，包含此次删除通知中包含的所有节点ID
    S = ['b1000', 'b1001', 'b1002']
    plaintext = {
        "affairs_id": "00001",
        "user_id": "u00001",
        "deleteGranularity": "age",
        "info_id": "a1b2c3d4e5",
        "from_bus_id": "b1000",
        "deleteMethod": "硬件删除"
    }
    # IBBE加密
    plaintext = dumps(plaintext)
    payload = encoder.ibbeEncode((S, PK, MSK), plaintext)
    print("payload加密内容如下:")

    print(payload)
    print(type(payload))
    payload = list(payload)

    # def convert_to_serializable(data):
    #     if isinstance(data, (list, tuple)):
    #         return [convert_to_serializable(item) for item in data]
    #     elif isinstance(data, dict):
    #         return {key: convert_to_serializable(value) for key, value in data.items()}
    #     else:
    #         return str(data)
    #
    # serializable_data = convert_to_serializable(payload)
    #
    # # 序列化
    # serialized = json.dumps(serializable_data)
    # print(serialized)
    #
    # url = f"http://127.0.0.1:20001/test6"
    # payload = json.dumps(payload)
    # requests.post(url, json=payload)



    # 解密测试
    # params = Parameters(params.__str__())
    # pairing1 = Pairing(params)
    # ID = 'b1000'
    #
    # Hdry = payload[0]
    # for i, (Hdr, y) in enumerate(Hdry):
    #     Hdr[0] = Element(pairing1, G1, Hdr[0])
    #     Hdr[1] = Element(pairing1, G2, Hdr[1])
    #     Hdry[i] = (Hdr, y)
    #
    # payload_list = list(payload)
    # payload_list[0] = Hdry
    # payload = tuple(payload_list)
    #
    # SK = Element(pairing1, G2, busid_to_IBBE_secret(ID))
    # pub_param = (S, SK, ID, PK)
    # try:
    #     newPlaintext = ibbeDecode(params, pairing1, pub_param, payload)
    #     print(newPlaintext)
    # except Exception as e:
    #     print(e)

    dataTransferPath = "成功！"

    payload = json.dumps(payload)
    return payload

if __name__ == "__main__":
    testacc.run(host='127.0.0.1', port=10000, debug=True)


# import json
# import sys
# import time
# from itertools import combinations
# from Crypto.Cipher import AES
# from Crypto.Util.Padding import pad, unpad
# from Crypto.Random import get_random_bytes
# from pypbc import *
#
# import hashlib
#
# # 使用 NIST P-256 标准的椭圆曲线参数
# # from sympy import randprime
#
#
# def setup(qbits, rbits, m):
#     """
#     初始化算法参数
#     @param qbits:
#     @param rbits:
#     @param m:
#     @return: 返回所需要的MSK以及PK
#     """
#     # 生成双线对参数
#     params = Parameters(qbits=qbits, rbits=rbits)
#
#     # 根据参数实例化双线性 对返回公共参数，PEKS是对称双线性对，G1=G2,二者的生成元是一样的，G2同样可以替换为G1
#     # 根据参数实例化双线性对
#     pairing = Pairing(params)
#
#     # g是G2的一个生成元
#     g = Element.random(pairing, G1)  # g是G2的一个生成元
#     h = Element.random(pairing, G2)
#
#     # MSK=【g，gama】
#     gama = Element.random(pairing, Zr)
#     MSK = [g, gama]
#
#     # 公钥是[w=g^gama, v = g*h...]
#     PK = []
#     w = Element(pairing, G1, value=g ** gama)
#     v = pairing.apply(g, h)
#     PK.append(w)
#     PK.append(v)
#
#     # 生成公钥剩余部分
#     for i in range(m + 1):
#         t = Element(pairing, G2, value=h ** (gama ** i))
#         PK.append(t)
#     return params, MSK, PK
#
#
# def hash_Zr(pairing, ID):
#     '''
#     hash操作，并将结果映射到Zr上
#     @param ID:用户身份
#     @return: 映射值
#     '''
#     hash_obj = hashlib.sha256(ID.encode())
#     hash_str = hash_obj.digest()
#     # 将二进制字符串转换为整数
#     h = int.from_bytes(hash_str, byteorder='big')
#     # 取模得到 Zp 中的值
#     return Element(pairing, Zr, value=h)
#
#
# def Extract(pairing, MSK, ID):
#     """
#     生成用户私钥的方法
#     @param pairing:双线性对 对象
#     @param MSK: MSK主密钥
#     @param ID: 用户身份
#     @return:
#     """
#     t = Element(pairing, Zr, value=hash_Zr(pairing, ID) + MSK[1]).__invert__()
#     SK = Element(pairing, G1, value=MSK[0] ** t)
#     return SK
#
#
# def IBBE_Encrypt(pairing, S: list, PK, MSK: list):
#     """
#     进行具体的加密
#     @param pairing:双线性对 对象
#     @param S: 含有参与加密的用户身份ID的list
#     @param PK:公钥
#     @param MSK:主密钥
#     @return: k一个list
#     """
#     k = Element.random(pairing, Zr)
#     C1 = Element(pairing, G1, value=PK[0] ** (k.__neg__()))
#     t = k
#     for ID in S:
#         t = Element(pairing, Zr, value=t * (MSK[1] + hash_Zr(pairing, ID)))
#     C2 = Element(pairing, G2, value=PK[2] ** (t))
#     K = Element(pairing, GT, value=PK[1] ** k)
#     Hdr = [C1, C2]
#     return Hdr, K
#
#
# def IBBE_Decrypt(pairing, S: list, SK, ID, Hdr, PK):
#     """
#     进行具体的IBBE解密
#     @param pairing: 双线性对 对象
#     @param S: 含有参与加密的用户身份ID的list
#     @param SK: 用户私钥
#     @param ID: 用户身份ID
#     @param Hdr: 含有[c1,c2]的list
#     @param PK: 公钥
#     @return: k 一个list
#     """
#     C1 = Hdr[0]
#     C2 = Hdr[1]
#     S_rm_val = [hash_Zr(pairing, i) for i in S if i != ID]
#     m = len(S_rm_val)
#     h_ps = Element.one(pairing, G2)
#     l = list(range(m))[::-1]
#     dict_pre = {}
#     dict_now = {}
#     for i in l:
#         if m - 1 == i:
#             h_ps = Element(pairing, G2, value=h_ps * PK[i + 2])
#             continue
#         if m - 2 == i:
#             c = list(combinations(range(m), m - i - 1))
#             sum1 = Element.zero(pairing, Zr)
#             for pair in c:
#                 sum = Element.one(pairing, Zr)
#                 for index in pair:
#                     sum = sum.__mul__(S_rm_val[index])
#                 sum1 = sum1.__add__(sum)
#                 name = str(json.dumps(pair))
#                 dict_now[name] = sum.__str__()
#             h_ps = h_ps.__mul__(Element(pairing, G2, value=PK[i + 2] ** sum1))
#             continue
#         dict_pre = dict_now
#         dict_now = {}
#         c = list(combinations(range(m), m - i - 1))
#         sum1 = Element.zero(pairing, Zr)
#         for pair in c:
#             name = json.dumps(pair)
#             pre_name = json.dumps(pair[:-1])
#             sum = Element(pairing, Zr, value=int(dict_pre[pre_name][2:], 16))
#             sum = sum.__mul__(S_rm_val[pair[-1]])
#             dict_now[name] = sum.__str__()
#             sum1 = sum1.__add__(sum)
#         h_ps = h_ps.__mul__(Element(pairing, G2, value=PK[i + 2] ** sum1))
#
#     t1 = pairing.apply(C1, h_ps)
#     t2 = pairing.apply(SK, C2)
#     t1t2 = Element(pairing, GT, value=t1 * t2)
#
#     s = Element.one(pairing, Zr)
#
#     for i in S_rm_val:
#         s = Element(pairing, Zr, s * i)
#
#     s = s.__invert__()
#     K = Element(pairing, GT, value=t1t2 ** s)
#
#     return K
#
#
# def Encrypt(pairing, S, PK, MSK: list, plaintext):
#     """
#     进一步使用IBBE生成的密钥k，使用k进一步生成用于加密密文的对称密钥key，
#     具体使用的加密方法为 AES
#     @param pairing:双线性对 对象
#     @param S:含有参与加密的用户身份ID的list
#     @param PK: 公钥
#     @param MSK: 主密钥
#     @param plaintext: 明文
#     @return:用于解密K的Hdr以及用于使用key解密出明文的iv以及密文
#     """
#     S.sort(reverse=False)
#     S_list = [S[i:i + 15] for i in range(0, len(S), 15)]
#     key = bytes.hex(get_random_bytes(32))
#     Hdry = []
#     iv = get_random_bytes(AES.block_size)
#     for S in S_list:
#         Hdri, Ki = IBBE_Encrypt(pairing, S, PK, MSK)
#         t = Ki[0] + Ki[1]
#         # 获得 32byte key
#         Ki = bytes.fromhex('{:032x}'.format(t % 2 ** 128))
#         # 生成随机的初始向量
#         cipher = AES.new(Ki, AES.MODE_CBC, iv)
#         yi = bytes.hex(cipher.encrypt(bytes.fromhex(key)))
#         Hdry.append((Hdri, yi))
#     plaintext = plaintext.encode()
#     iv1 = get_random_bytes(AES.block_size)
#     padded_plaintext = pad(plaintext, AES.block_size)
#     cipher = AES.new(bytes.fromhex(key), AES.MODE_CBC, iv1)
#     ciphertext = cipher.encrypt(padded_plaintext)
#     return Hdry, bytes.hex(iv), ((bytes.hex(iv1), bytes.hex(ciphertext)))
#
#
# def Decrypt(pairing, S: list, SK, ID, Hdry, PK, iv, ciphertext):
#     """
#     IBBE分组加密
#     @param pairing:
#     @param S:
#     @param SK:
#     @param ID:
#     @param Hdry:
#     @param PK:
#     @param iv:
#     @param ciphertext:
#     @return:
#     """
#     S.sort(reverse=False)
#     S_list = [S[i:i + 15] for i in range(0, len(S), 15)]
#     i = 0
#     for i, S in enumerate(S_list):
#         if ID in S:
#             break
#     S = S_list[i]
#     Hdr, yi = Hdry[i]
#
#     iv = bytes.fromhex(iv)
#     iv1 = bytes.fromhex(ciphertext[0])
#
#     ciphertext = bytes.fromhex(ciphertext[1])
#     Ki = IBBE_Decrypt(pairing, S, SK, ID, Hdr, PK)
#     t = Ki[0] + Ki[1]
#     # 获得 32byte key
#     Ki = bytes.fromhex('{:032x}'.format(t % 2 ** 128))
#     decipher = AES.new(Ki, AES.MODE_CBC, iv)
#     key = decipher.decrypt(bytes.fromhex(yi))
#
#     decipher = AES.new(key, AES.MODE_CBC, iv1)
#
#     decrypted_padded_plaintext = decipher.decrypt(ciphertext)
#     # 对解密后的明文进行去填充
#     decrypted_plaintext = unpad(decrypted_padded_plaintext, AES.block_size)
#     return decrypted_plaintext.decode()
#
#
# from flask import Flask
#
# app = Flask(__name__)
#
#
# @app.route('/hello', methods=['GET'])
# def hello():
#     params, MSK, PK = setup(qbits=512, rbits=160, m=30)
#     pairing = Pairing(params)
#     SK_0 = Extract(pairing, MSK, 'b1000')
#     # 测试从1到25开始测试
#     time_list = []
#     for i in range(1, 10):
#         S = []
#         for j in range(i):
#             name = 'b' + str(1000 + j)
#             S.append(name)
#         plaintext = 'hello world'
#         Hdry, iv, cipthertext = Encrypt(pairing, S, PK, MSK, plaintext)
#         t1 = time.time() * 1000
#         new_plaintext = Decrypt(pairing, S, SK_0, 'b1000', Hdry, PK, iv, cipthertext)
#         t2 = time.time() * 1000
#         print(new_plaintext + str(i), " ", t2 - t1)
#     return "Yes"
#
#
# if __name__ == '__main__':
#     app.run(debug=True, port=5000, host="127.0.0.1")