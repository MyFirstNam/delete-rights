import hashlib


def hmac(key, msg):
    """
    HMAC（Hash-based Message Authentication Code）是一种常见的消息认证码算法，它可以用于验证消息的完整性和真实性。它基于哈希函数和密钥来生成一个固定长度的验证码。
    SM3是中国自主设计的密码杂凑算法，其设计思想和SHA-256等哈希算法类似，但具有更高的安全性和更好的性能。HMAC-SM3是基于SM3的HMAC算法，它的原理如下：
    对于给定的密钥K和消息M，首先需要对密钥进行处理。如果密钥长度超过SM3算法的分组长度（即64字节），则需要对密钥进行哈希处理，得到一个长度为32字节的密钥K'。如果密钥长度不足，则需要在其后面补0，直到达到分组长度。
    然后需要定义两个常数：ipad和opad。它们分别用于对密钥进行前置和后置填充，并且是固定的。
    对于ipad和opad，分别对其进行异或操作，得到两个新的密钥：K1 = K' XOR ipad，K2 = K' XOR opad。
    将消息M分别与K1和K2进行拼接，并对拼接后的结果进行SM3哈希运算，得到两个哈希值：H1 = SM3(K1 || M)，H2 = SM3(K2 || H1 || M)。
    最终的HMAC值就是H2。
    总之，HMAC-SM3算法的核心思想是将密钥和消息进行组合，并通过哈希函数来生成验证码。它的安全性取决于哈希函数的安全性和密钥的长度。
    :param key:会经过处理变成64字节
    :param msg:需要mac的信息
    :return:哈希后的结果
    """
    block_size = 64
    if len(key) > block_size:
        key = hashlib.sha256(key).digest()
    key = key.ljust(block_size, b'\0')
    o_key_pad = bytes([x ^ 0x5c for x in key])
    i_key_pad = bytes([x ^ 0x36 for x in key])
    hash_inner = hashlib.sha256(i_key_pad + msg).digest()
    hash_outer = hashlib.sha256(o_key_pad + hash_inner).digest()
    return hash_outer
