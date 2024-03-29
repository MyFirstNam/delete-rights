import json
import requests
import csv
import datetime
import pprint
from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS

userroute = Flask(__name__)
CORS(userroute)  # 启用 CORS

# 辅助函数
def print_with_timestamp(message):
    current_time = datetime.datetime.now()
    timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


# 用户类
class User:
    # 功能：发出删除意图（一个字典）
    def __init__(self, user_id):
        self.user_id = user_id

    def deleteIntention(self, affairs_id: str, deleteGranularity: str, info_id: str, init_bus_id: str,
                        deleteMethod: str):
        """
        模拟用法发起删除意图请求，请求发往route_bus
        :param affairs_id:
        :param deleteGranularity:
        :param info_id:
        :param source_bus_id:
        :param deleteMethod:
        :return:
        """
        delintention = {
            "affairs_id": affairs_id,
            "user_id": self.user_id,
            "deleteGranularity": deleteGranularity,
            "info_id": info_id,
            "source_bus_id": init_bus_id,
            "deleteMethod": deleteMethod
        }
        print_with_timestamp(f'用户{self.user_id}发起删除意图请求，删除意图内容如下:')
        pprint.pprint(delintention)
        return delintention

    def setTimeLimit(self, affairs_id: str, deleteGranularity: str, info_id: str, init_bus_id: str, time_limit: float,
                     deleteMethod: str):
        """
        对存放数据的数据库进行时间限制
        :param affairs_id:
        :param info_id:
        :param time_limit:
        :return:
        """
        delintention = {
            "affairs_id": affairs_id,
            "user_id": self.user_id,
            "deleteGranularity": deleteGranularity,
            "info_id": info_id,
            "source_bus_id": init_bus_id,
            "time_limit": time_limit,
            "deleteMethod": deleteMethod
        }
        print_with_timestamp(f'用户{self.user_id}发起删除意图请求，删除意图内容如下:')
        pprint.pprint(delintention)
        return delintention

    # def setCountLimit(self,affairs_id:str,info_id:str,count_limit:int):
    def setCountLimit(self, affairs_id: str, deleteGranularity: str, info_id: str, init_bus_id: str, count_limit: int,
                      deleteMethod: str):
        """
        对存放数据的数据库进行流转次数限制
        :param affairs_id:
        :param info_id:
        :param count_limit:
        :return:
        """
        delintention = {
            "affairs_id": affairs_id,
            "user_id": self.user_id,
            "deleteGranularity": deleteGranularity,
            "info_id": info_id,
            "source_bus_id": init_bus_id,
            "count_limit": count_limit,
            "deleteMethod": deleteMethod
        }
        print_with_timestamp(f'用户{self.user_id}发起删除意图请求，删除意图内容如下:')
        pprint.pprint(delintention)
        return delintention

    def sendintention(self, delintention):
        with open('ID.csv', 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['ID'] == delintention["source_bus_id"]:
                    port = row['port']
                    ip = row['IP']

        delintention = json.dumps(delintention)
        url = f"http://{ip}:{port}/test/postx/endpointx"  # 替换为自己的实际目标URL
        # response = requests.post(url, json=delintention)
        # # 检查响应
        # if response.status_code == 200:
        #     print("POST请求成功")
        #     print(response.text)
        # else:
        #     print("POST请求失败")
        #     print("响应状态码:", response.status_code)

        max_retries = 3  # 最大重试次数
        for _ in range(max_retries):
            response = requests.post(url, json=delintention)
            # 检查响应
            if response.status_code == 200:
                print_with_timestamp("本用户发起删除意图的POST请求成功！")
                # print_with_timestamp("响应状态码: " + response.text)
                break  # 如果成功，跳出循环
            else:
                print_with_timestamp("本用户发起删除意图的POST请求失败！")
                print_with_timestamp("响应状态码: " + str(response.status_code))

        # 循环完仍未成功
        else:
            print_with_timestamp("循环发送请求达到最大重试次数，仍未成功！")


# userroute = Flask(__name__)


@userroute.route("/user/postx/endpointx", methods=['POST'])
# POST格式为JSON格式
def intentionAly():
    # 通过判断post是否包含time、count字段，来调用DelTrigger中不同的函数
    data = request.json
    print(data)
    return ""


@userroute.route('/userpost', methods=['POST'])
def delPost():
    data = request.json
    # data: dict
    # TODO 传入数据用data中的值替换，参数名和键对应
    delintention = user.deleteIntention("0002", "age", "0x2221", "b1000", "硬件删除")
    user.sendintention(delintention)
    return {"status": "success"}, 200  # 发送响应


if __name__ == "__main__":
    user = User("b00001")
    # delintention = user.deleteIntention("0002", "age", "0x2221", "b1000", "硬件删除")
    # # delintention = user.setTimeLimit("0001", "软件删除", "0x0003", "b1000", 10, "按需")
    # user.sendintention(delintention)
    userroute.run(host='127.0.0.1', port=30000)

    # 在本地跑把这两行注释掉
    # delintention = user.deleteIntention("0002", "age", "0x2221", "b1000", "硬件删除")
    # user.sendintention(delintention)
