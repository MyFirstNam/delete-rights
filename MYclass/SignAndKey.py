import csv
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization

#公钥查询
def query_Publickey_pair_by_id(csv_filename, identifier):
    with open(csv_filename, mode='r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            if row["ID"] == identifier:
                return row["Public Key"]
    return None

#私钥查询
def query_Privatekey_pair_by_id(csv_filename, identifier):
    with open(csv_filename, mode='r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            if row["ID"] == identifier:
                return row["Private Key"]
    return None

# 使用私钥进行签名
def sign_message(private_key_pem, hash_message):
    private_key = serialization.load_pem_private_key(
        private_key_pem.encode(),
        password=None
    )

    # 将消息签名
    signature = private_key.sign(
        hash_message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    return signature


# 使用公钥进行签名验证
def verify_signature(public_key_pem, hashed_message, signature):
    public_key = serialization.load_pem_public_key(
        public_key_pem.encode()
    )

    try:
        public_key.verify(
            signature,
            hashed_message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True  # 验证成功
    except:
        return False  # 验证失败
