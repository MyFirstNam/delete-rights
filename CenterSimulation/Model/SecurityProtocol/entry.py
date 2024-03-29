from pypbc import *
import hashlib
from json import dumps
from itertools import combinations
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from Crypto.Random import get_random_bytes

# 解密


# ibbe解密
def ibbeDecode(params, pairing, pub_param, payload: tuple):
    """
    pub_param：公共参数 类型：元组tuple
    payload:也是一个使用ibbeEncode加密产生的返回值 类型：元组tuple
    return:字符串明文 类型：str
    """
    if (params == None):
        print("未设置params，请设置后在使用当前方法！")
        return

    # 解密公共参数  S,SK,ID,PK
    S, SK, ID, PK = pub_param

    # 解析payload  Hdry, iv, ciphertext（其实就是加密得到的结果）
    Hdry, iv, ciphertext = payload[0], payload[1], payload[2]

    # 解析公共参数

    # 对用户id排序后进行分组
    S.sort(reverse=False)
    S_list = [S[i:i + 15] for i in range(0, len(S), 15)]
    i = 0

    # 找出当前用户属于哪一个子list
    for i, S in enumerate(S_list):
        if ID in S:
            break

    # 找出那一组对应的解密参数
    S = S_list[i]
    Hdr, yi = Hdry[i]

    iv = bytes.fromhex(iv)
    iv1 = bytes.fromhex(ciphertext[0])

    ciphertext = bytes.fromhex(ciphertext[1])
    Ki = IBBE_Decrypt(pairing, S, SK, ID, Hdr, PK)
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
def IBBE_Decrypt(pairing, S: list, SK, ID, Hdr, PK):
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
    S_rm_val = [hash_Zr(pairing, i) for i in S if i != ID]
    m = len(S_rm_val)
    h_ps = Element.one(pairing, G2)
    l = list(range(m))[::-1]
    dict_pre = {}
    dict_now = {}
    # count 用来统计循环数量
    count = 0
    for i in l:
        # count+=1
        # print(count)
        if m - 1 == i:
            h_ps = Element(pairing, G2, value=h_ps * PK[i + 2])
            continue
        if m - 2 == i:
            c = list(combinations(range(m), m - i - 1))
            sum1 = Element.zero(pairing, Zr)
            for pair in c:
                sum = Element.one(pairing, Zr)
                for index in pair:
                    sum = sum.__mul__(S_rm_val[index])
                sum1 = sum1.__add__(sum)
                name = str(dumps(pair))
                dict_now[name] = sum.__str__()
            h_ps = h_ps.__mul__(Element(pairing, G2, value=PK[i + 2] ** sum1))
            continue
        dict_pre = dict_now
        dict_now = {}
        c = list(combinations(range(m), m - i - 1))
        sum1 = Element.zero(pairing, Zr)
        for pair in c:
            # count+=1
            # print(count)
            name = dumps(pair)
            pre_name = dumps(pair[:-1])
            sum = Element(pairing, Zr, value=int(dict_pre[pre_name][2:], 16))
            sum = sum.__mul__(S_rm_val[pair[-1]])
            dict_now[name] = sum.__str__()
            sum1 = sum1.__add__(sum)
        h_ps = h_ps.__mul__(Element(pairing, G2, value=PK[i + 2] ** sum1))
    t1 = pairing.apply(C1, h_ps)
    t2 = pairing.apply(SK, C2)
    t1t2 = Element(pairing, GT, value=t1 * t2)

    s = Element.one(pairing, Zr)

    for i in S_rm_val:
        # count+=1
        # print(count)
        s = Element(pairing, Zr, s * i)

    s = s.__invert__()
    K = Element(pairing, GT, value=t1t2 ** s)

    return K

def hash_Zr(pairing, ID):
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
    return Element(pairing, Zr, value=h)

