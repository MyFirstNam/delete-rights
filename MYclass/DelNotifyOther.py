import asyncio    # todo 异步发送的时候改为aiohttps库
import copy
import json
import csv
import pprint
import time
import aiohttp
import httpx
import datetime
from HMACverify import generate_hmac

def print_with_timestamp(message):
    current_time = datetime.datetime.now()
    timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

# 此类负责判断有几个子节点，负责启动几个异步函数
class CountSend:
    def __init__(self, nextNode, delNotice: dict):
        self.nextNode = nextNode
        self.delNotice = delNotice

    async def delNotifyOther(self, ip, port, delNotice, item):
        # 直接给指定IP和指定port发送删除通知delNotice
        # 发送POST请求
        # delNotice = json.dumps(delNotice)
        # url = f"http://{ip}:{port}/test/postx/endpointx"
        # async with httpx.AsyncClient() as client:
        #     try:
        #         response = await client.post(url, json=delNotice)
        #         response.raise_for_status()  # 检查响应状态码
        #         print("给" + port + "节点发送删除通知成功!")
        #         return response.text
        #     except httpx.HTTPError as e:
        #         print(f"HTTP请求失败，给子节点发送删除通知失败！{e}")
        #         return None
        # todo 在这里进行删除通知发送失败异常上报
        delNotice = json.dumps(delNotice)
        url = f"http://{ip}:{port}/test/postx/endpointx"

        with open('keyserect.CSV', 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['ID'] == item:
                    secret_key = row['Serect']
        hmac_code = generate_hmac(delNotice, secret_key)
        # 请求头中包含消息验证码
        headers = {"HMAC": hmac_code.hex(), "Content-Type": "application/json"}
        max_retries = 3  # 最大重试次数
        for _ in range(max_retries):
            try:
                async with httpx.AsyncClient() as client:
                    print_with_timestamp("——————————————————————————————删除通知分发——————————————————————————————")
                    response = await client.post(url, json=delNotice, headers=headers)
                    response.raise_for_status()
                    print_with_timestamp(f"给企业对应的网络地址 {url} 发送删除通知成功!")
                    print_with_timestamp(f"本次发送删除通知内容如下:")
                    pprint.pprint(json.loads(delNotice))
                    # print(response.text)
                    return response.text
            except httpx.HTTPError as e:
                print_with_timestamp(f"第 {_} 次 HTTP请求失败，给子节点发送删除通知失败！错误代码:{e}")
        print_with_timestamp(f"系统尝试发送 {max_retries} 次后，仍未发送成功！")
        return None

    # 此函数中的IP和port通过子节点的唯一标识符ID查询而来，循环添加
    async def sendnotice(self):
        newdelNoticeList = []
        for item in self.nextNode:
            with open('ID.csv', 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row['ID'] == item:  # 默认中心监管机构的ID是b1999
                        port = row['port']
                        ip = row['IP']
                        break
            delNotice = copy.deepcopy(self.delNotice)                 #!!!!!!!!!!!!!!!!!进行深度拷贝
            delNotice["to_bus_id"] = item                             # 把删除通知中的“to_bus_id"信息补充完整
            newdelNoticeList += [(ip, port, delNotice, item)]
        coroutines = [asyncio.create_task(self.delNotifyOther(x, i, j, t)) for x, i, j, t in newdelNoticeList]
        await asyncio.wait(coroutines)

    def runtest(self):
        asyncio.run(self.sendnotice())


