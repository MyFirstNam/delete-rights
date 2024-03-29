import sys
from gmssl import sm4

class my_sm4_ecb:
    def __init__(self,key,mode:int):
        # mode==2：ECB，mode == 3：CTR
        self.SM2_PRIVATE_KEY = key

    # 加密
    def encrypt(self,info: bytes):
        encode_info = self.sm2_crypt.encrypt(info)
        # encode_info = b64encode(encode_info).decode()  # 将二进制bytes通过base64编码
        return encode_info

    # 解密
    def decrypt(self,info:bytes):
        # info = b64decode(info.encode())  # 通过base64解码成二进制bytes
        decode_info = self.sm2_crypt.decrypt(info)
        return decode_info


if __name__ == "__main__":
    print("123"[:-1])
