import json
import requests
import sys
sys.path.append('/home/dengx/deng_delete2_6/')

from flask import Flask, request, jsonify, Blueprint
import json
from CenterSimulation.Utils.IBBEKeyRead import IBBEKeyRead, collect_node_values
from CenterSimulation.Model.SecurityProtocol import MessageEncoder
from CenterSimulation.Model.SecurityProtocol import MessageDecoder
from CenterSimulation.Model.SecurityProtocol.protocol_utils.busid_to_secret import busid_to_IBBE_secret
from CenterSimulation.Model.SecurityProtocol.entry import ibbeDecode
import requests
from pypbc import *
import hashlib
from json import dumps
from itertools import combinations
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad, pad
from Crypto.Random import get_random_bytes

# 目标 URL
# url = f"http://127.0.0.1:10001/process"
url = f"http://127.0.0.1:20000/enterprise/receive_user"
# 要发送的数据
data = {
    "affairs_id": "00001",
    "user_id": "u00001",
    "deleteGranularity": "age",
    "info_id": "a1b2c3d4e5",
    "source_bus_id": "b0001",
    "time_limit": "",  # 时间限制为可选字段，不是每次内容都有，”“空字符表示没有时间显示
    "count_limit": 0,  # 次数限制为可选字段，不是每次内容都有,0表示没有次数限制
    "deleteMethod": "yingjianshanchu"
}

data = json.dumps(data)
# 发送 POST 请求
response = requests.post(url, json=data)

# 打印响应内容
print("Status Code:", response.status_code)
print("Response Body:", response.text)


# 目标 URL
# url = f"http://127.0.0.1:10001/process"
# url = f"http://127.0.0.1:20000/center/receive_path"
# url = f"http://127.0.0.1:10000/tree/postx/endpointx"
# #
# # 要发送的数据
# data = {
#     "affairs_id": "00001",
#     "user_id": "u00001",
#     "deleteGranularity": "age",
#     "info_id": "a1b2c3d4e5",
#     "from_bus_id": "b1000",
#     "deleteMethod": "硬件删除"
# }
# data = json.dumps(data)
# # 发送 POST 请求
# response = requests.post(url, json=data)
#
# # 打印响应内容
# print("Status Code:", response.status_code)
# print("Response Body:", response.text)

# payload = response.text
# payload = json.loads(payload)
# print(type(payload))
#
# # 解密测试
# params, MSK, PK = IBBEKeyRead()
# params = Parameters(params.__str__())
#
# S = ['b1000', 'b1001', 'b1002']
# ID = 'b1000'
# pairing1 = Pairing(params)
# SK = Element(pairing1, G2, busid_to_IBBE_secret(ID))
# # pub_param = (S, SK, ID, PK)
# # print("ok")
# # try:
# #     newPlaintext = ibbeDecode(params, pairing1, pub_param, payload)
# #     print(newPlaintext)
# # except Exception as e:
# #     print(e)
#
# ID = 'b1000'
# payload = tuple(payload)
# print(payload)
# print(type(payload))
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
# pub_param = (S, SK, ID, PK)
#
# # try:
# #     newPlaintext = ibbeDecode(params, pairing1, pub_param, payload)
# #     print(newPlaintext)
# #     print(type(newPlaintext))
# # except Exception as e:
# #     print(e)
# decoder = MessageDecoder.Decoder()
# decoder.setParams(params.__str__())
# try:
#     newPlaintext = decoder.ibbeDecode(pub_param, payload)
#     print(bytes(newPlaintext, "utf-8").decode("unicode-escape"))
# except Exception as e:
#     print(e)

# request.py
# import requests
#
# url = 'http://127.0.0.1:5000/hello'

# response = requests.get(url)
# print(response.text)
