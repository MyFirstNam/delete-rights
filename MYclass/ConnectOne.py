import requests
import json
import datetime
def print_with_timestamp(message):
    current_time = datetime.datetime.now()
    timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

class ConnectOne:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = int(port)

    def reqPah(self, affairs_id, info_id):
        """
        向课题一获取删除流转路径，访问课题一的路由，返回json，
        :param affairs_id:
        :param info_id:
        :return: 路由访问返回的json中的dataTransferPath字段,实际上是个list【】
        "data": {
        "infoID": "283749abaa234cde",
                "dataTransferPath": [
            { "from": "b1000", "to": "b1001" },
            { "from": "b1001", "to": "b1002" },
            { "from": "b1002", "to": "b1003" }
            ]
        }
        """
        print_with_timestamp(f'向中心监管机构请求info为{info_id}的信息流转记录，此次事务的id为{affairs_id}')
        reqTree = f"企业请求info为{info_id}的信息流转记录，此次事务的id为{affairs_id}"
        reqTree = json.dumps(reqTree)
        url = f"http://{self.ip}:{self.port}/tree/postx/endpointx"

        max_retries = 3  # 最大重试次数
        for _ in range(max_retries):
            response = requests.post(url, json=reqTree)
            # 检查响应
            if response.status_code == 200:
                print_with_timestamp("本企业向中心监管机构发起数据流转路径的POST请求成功！")
                return response.text
                break  # 如果成功，跳出循环
            else:
                print_with_timestamp("本企业向中心监管机构发起数据流转路径的POST请求失败！")
                print_with_timestamp("响应状态码: " + str(response.status_code))
                return response.status_code
        # 循环完仍未成功
        else:
            print_with_timestamp("循环发送请求达到最大重试次数，仍未成功！")
            return ""