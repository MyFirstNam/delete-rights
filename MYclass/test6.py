# import datetime
# current_time = datetime.datetime.now()
# timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
# print(timestamp)
# print(type(timestamp))
import json

# my_dict = {'name': 'John', 'age': 30, 'address': '123 Main St'}
#
# # 删除键是'address'的键值对，并获取其值
# removed_value = my_dict.pop('asdasda','Not Found')
#
# print(my_dict)
# print("Removed value:", removed_value)

from flask import Flask, request
import jsonpickle
import sys
sys.path.append('/home/dengx/deng_delete2_6/')

from flask import Flask, request, jsonify, Blueprint
import json
from CenterSimulation.Utils.IBBEKeyRead import IBBEKeyRead, collect_node_values
from CenterSimulation.Model.SecurityProtocol import MessageEncoder
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


test6 = Flask(__name__)


@test6.route("/test6", methods=["POST"])
def test6123():
    data = request.data
    payload = json.loads(data)
    payload = tuple(payload)
    print(payload)
    print(type(payload))


    # 解密测试
    params, MSK, PK = IBBEKeyRead()
    params = Parameters(params.__str__())

    S = ['b1000', 'b1001', 'b1002']
    ID = 'b1000'
    pairing1 = Pairing(params)
    SK = Element(pairing1, G2, busid_to_IBBE_secret(ID))
    # pub_param = (S, SK, ID, PK)
    # print("ok")
    # try:
    #     newPlaintext = ibbeDecode(params, pairing1, pub_param, payload)
    #     print(newPlaintext)
    # except Exception as e:
    #     print(e)

    ID = 'b1000'

    Hdry = payload[0]
    for i, (Hdr, y) in enumerate(Hdry):
        Hdr[0] = Element(pairing1, G1, Hdr[0])
        Hdr[1] = Element(pairing1, G2, Hdr[1])
        Hdry[i] = (Hdr, y)

    payload_list = list(payload)
    payload_list[0] = Hdry
    payload = tuple(payload_list)
    pub_param = (S, SK, ID, PK)
    try:
        newPlaintext = ibbeDecode(params, pairing1, pub_param, payload)
        print(newPlaintext)
    except Exception as e:
        print(e)

    return "ok"


if __name__ == "__main__":
    test6.run(host='127.0.0.1', port=20001, debug=True)
