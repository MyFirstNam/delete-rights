import hmac
import hashlib
from gmssl import sm3, func


# def generate_hmac(message, key):
#     hash_function = hashlib.sha256
#     hmac_object = hmac.new(key.encode(), message.encode(), hash_function)
#     hmac_code = hmac_object.digest()
#     return hmac_code
#
#
# def verify_hmac(message, key, received_hmac):
#     hash_function = hashlib.sha256
#     hmac_object = hmac.new(key.encode(), message.encode(), hash_function)
#     expected_hmac = hmac_object.digest()
#     return hmac.compare_digest(expected_hmac, bytes.fromhex(received_hmac))


def generate_hmac(message, key):
    generated_mac = hmac_sm3(key=key.encode(), message=message.encode())
    print("Gen:", message, key)
    return generated_mac.encode()


# TODO: debug
# 调用这个函数前，传入的received_hmac为原始生成的mac，即需要bytes.fromhex(received_hmac)
# 然后函数中最后一行的bytes.fromhex(received_hmac)替换为received_hmac
# 然后测试main样例和你的系统
def verify_hmac(message, key, received_hmac):
    current_mac = hmac_sm3(key=key.encode(), message=message.encode())
    # 比较当前MAC与预期MAC
    return current_mac.encode() == bytes.fromhex(received_hmac)


def hmac_sm3(key, message):
    blocksize = 64  # SM3的块大小为64字节

    # 如果key太长，先用SM3进行哈希
    if len(key) > blocksize:
        key = bytes.fromhex(sm3.sm3_hash(func.bytes_to_list(key)))

    # 补齐key到块大小
    key += b'\x00' * (blocksize - len(key))

    # 内部和外部填充
    ipad = bytearray([0x36] * blocksize)
    opad = bytearray([0x5C] * blocksize)

    # 分别与key进行XOR
    ki = bytearray([x ^ y for x, y in zip(key, ipad)])
    ko = bytearray([x ^ y for x, y in zip(key, opad)])

    # 内部哈希
    inner_hash = sm3.sm3_hash(func.bytes_to_list(ki + message))

    # 外部哈希
    hmac = sm3.sm3_hash(func.bytes_to_list(ko + bytearray.fromhex(inner_hash)))

    return hmac


if __name__ == '__main__':
    # 使用提供的函数和示例数据生成MAC
    key = 'secret key'
    message = 'Hello, this is a test message.'
    generated_mac = generate_hmac(message, key)
    print("Generated SM3 HMAC:", generated_mac)

    # 校验MAC
    if verify_hmac(message, key, generated_mac):
        print("MAC verification successful. Message is authentic and intact.")
    else:
        print("MAC verification failed. Message is not authentic.")
