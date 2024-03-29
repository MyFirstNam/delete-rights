import sys
from gmssl import sm2
# sm2的公私钥
class my_sm2:
    def __init__(self,SM2_PRIVATE_KEY = '00B9AB0B828FF68872F21A837FC303668428DEA11DCD1B24429D0C99E24EED83D5',SM2_PUBLIC_KEY = 'B9C9A6E04E9C91F7BA880429273747D7EF5DDEB0BB2FF6317EB00BEF331A83081A6994B8993F3F5D6EADDDB81872266C87C018FB4162F5AF347B483E24620207'):
        self.SM2_PRIVATE_KEY = SM2_PRIVATE_KEY
        self.SM2_PUBLIC_KEY = SM2_PUBLIC_KEY
        self.sm2_crypt = sm2.CryptSM2(public_key=SM2_PUBLIC_KEY, private_key=SM2_PRIVATE_KEY)

    # 加密
    def encrypt(self,info:bytes):
        encode_info = self.sm2_crypt.encrypt(info)
        # encode_info = b64encode(encode_info).decode()  # 将二进制bytes通过base64编码
        return encode_info

    # 解密
    def decrypt(self,info:bytes):
        # info = b64decode(info.encode())  # 通过base64解码成二进制bytes
        decode_info = self.sm2_crypt.decrypt(info)
        return decode_info


if __name__ == "__main__":
    contact_info = b"helloworld!"
    sm2_enc = my_sm2()
    encrypted_contact_info = sm2_enc.encrypt(contact_info)
    print(contact_info)
    decrypted_contact_info = sm2_enc.decrypt(encrypted_contact_info)
    print(decrypted_contact_info)
