# 异步函数功能实现
import pprint

import httpx
import SignAndKey
import DelNotifyOther
import json
import hashlib
import csv
import datetime
from ConnectSysDel import ConnectSysDel
from Json2Tree import json2tree
import time

# print_with_timestamp 函数的功能是为了在输出信息中增加时间信息
# 输入要打印的信息
# 输出加了时间戳的信息
def print_with_timestamp(message):
    current_time = datetime.datetime.now()
    timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

# 此异步函数是执行当前节点除去删除通知验证后的其他操作，包括删除通知转发与删除指令分解分发
# 输入删除通知与Bus_id
# 函数输出为返回值，在函数中会执行相关操作
async def processNotify(delnotice, Bus_id: str):
    # (1)从参数中提取数据，接收的是删除通知和本节点Bus_id
    delNotice = delnotice
    # print_with_timestamp(f'本企业{Bus_id}已经成功接收得到来自于上一条删除通知')
    # print_with_timestamp("——————————————————————————————删除通知生成——————————————————————————————")
    # print_with_timestamp(f'本企业{Bus_id}生成的删除通知内容如下：')
    # pprint.pprint(delNotice)
    # (2) 调用ConConnectSysDel类中的函数得到删除指令，并且发送给确定性删除系统
    ip = "202.243.25.166"  # 模拟域0中确定性删除系统的ip和port
    port = 9650
    # connectsysdel = ConnectSysDel(ip, port)
    # delInstruction = connectsysdel.buildDelIns(delnotice)
    start = time.time()
    for i in range(10000):
        connectSysdel = ConnectSysDel(ip, port)   # 传入确定性删除系统的IP和port
        delInstruction = connectSysdel.buildDelIns(delNotice)
    end = time.time()
    print_with_timestamp("——————————————————————————————删除指令生成——————————————————————————————")
    print_with_timestamp('删除指令已经成功生成！')
    # print_with_timestamp(f"10000条删除指令生成时间为: {(end - start) * 1000} ms")
    response = connectSysdel.sendDelIns(delInstruction)
    print_with_timestamp("——————————————————————————————删除指令分发——————————————————————————————")
    print_with_timestamp(response)


    # start = time.time()
    # for i in range(10000):
    #     connectSysdel = ConnectSysDel(ip, port)   # 传入确定性删除系统的IP和port
    #     delInstruction = connectSysdel.buildDelIns(delNotice)
    # end = time.time()
    # print("删除指令生成时间为: %s ms"%((end-start)*1000))

    # (3)删除通知分发
    # 首先根据自己当前节点的位置，通过deleteNotifyTree, 得到后继节点，即后面应该发给那些节点
    tree = json2tree(delNotice["deleteNotifyTree"])
    nextnode = [i._identifier for i in tree.children(Bus_id)]

    # (3-1)不是叶子节点，转发新的删除通知（不修改删除通知树，因为删除通知确认需要回溯）
    if nextnode != []:
        delNotice = {
            "affairs_id": delNotice["affairs_id"],
            "user_id": delNotice["user_id"],
            "info_id": delNotice["info_id"],
            "from_bus_id": Bus_id,
            "to_bus_id": "",
            "deleteMethod": delNotice["deleteMethod"],
            "deleteGranularity": delNotice["deleteGranularity"],
            "deleteNotifyTree": delNotice["deleteNotifyTree"]  # 一个字典
        }
        print_with_timestamp(f"本企业{Bus_id}对于本条信息的后续'子节点企业'为{nextnode}")
        await DelNotifyOther.CountSend(nextnode, delNotice).sendnotice()

    # 后继节点为空
    # (3-2) 是叶子节点
    else:
        # 如果后继节点是空，表示自己是叶子节点，则不需要继续发送，需要生成自己的删除通知确认，并根据接收到的删除通知中的deleteNotifyTree找到自己的父节点，将删除通知确认发送给父节点
        # 关于如何发送，就是访问父节点的delConfirmAcc路由
        print_with_timestamp(f"本企业{Bus_id}对于本条信息的后续节点为空！")
        print_with_timestamp("——————————————————————————————删除通知确认生成——————————————————————————————")
        print_with_timestamp(f"开始生成删除通知确认信息")

        csv_filename = "key_pairs.csv"
        identifier_to_query = Bus_id
        private_key_pem = SignAndKey.query_Privatekey_pair_by_id(csv_filename, identifier_to_query)

        # 这里的DelConfirm其实应该如下这样的。因为自己是叶子节点，后续没有签名了，那部分应该是空
        tree = json2tree(delNotice["deleteNotifyTree"])
        node = tree.parent(Bus_id)

        if node is not None:
            node = node._identifier
            print_with_timestamp(f"本企业{Bus_id}对于本条信息的'父节点企业'为{node}")
            DelConfirm_1 = {
                "affairs_id": delNotice["affairs_id"],
                "from_bus_id": Bus_id,
                "to_bus_id": node,
                "user_id": delNotice["user_id"],
                "info_id": delNotice["info_id"],
                "deleteNotifyTree": delNotice["deleteNotifyTree"],
            }
            delconfirmstr = json.dumps(DelConfirm_1)
            hash_object = hashlib.sha256()
            hash_object.update(delconfirmstr.encode("utf-8"))
            hash_result = hash_object.digest()
            signature = SignAndKey.sign_message(private_key_pem, hash_result)

            # 下面这一行应该是给其父节点发送删除通知确认
            DelConfirm = {
                "affairs_id": delNotice["affairs_id"],
                "from_bus_id": Bus_id,
                "to_bus_id": node,
                "user_id": delNotice["user_id"],
                "info_id": delNotice["info_id"],
                "deleteNotifyTree": delNotice["deleteNotifyTree"],
                "DelConfirmSignatureDict": {Bus_id: signature}
            }
            print_with_timestamp("——————————————————————————————删除通知确认回送——————————————————————————————")
            # 此处的ip和port应该通过父节点的ID去查找
            with open('ID.csv', 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row['ID'] == node:
                        port = row['port']
                        ip = row['IP']

            # 签名内容需要转换为十六进制
            hex_string = DelConfirm["DelConfirmSignatureDict"][Bus_id].hex()
            DelConfirm["DelConfirmSignatureDict"][Bus_id] = hex_string
            DelConfirm = json.dumps(DelConfirm)
            url = f"http://{ip}:{port}/confirm/postx/endpointx"  # 替换为自己的实际目标URL
            print_with_timestamp(f'发送删除通知确认的网络路径为：{url}')

            # async with httpx.AsyncClient() as client:
            #     try:
            #         response = await client.post(url, json=DelConfirm)
            #         response.raise_for_status()  # 检查响应状态码
            #         print("给" + str(port) + "节点发送删除通知确认成功！")
            #         return response.text
            #     except httpx.HTTPError as e:
            #         print(f"HTTP请求失败：{e}")
            #         return
            # todo 在这里进行删除通知确认异常上报
            max_retries = 3  # 最大重试次数
            for _ in range(max_retries):
                try:
                    async with httpx.AsyncClient() as client:
                        response = await client.post(url, json=DelConfirm)
                        response.raise_for_status()  # 检查响应状态码
                        print_with_timestamp(f"给'父节点'企业发送删除通知确认成功!")
                        return response.text
                except httpx.HTTPError as e:
                    print_with_timestamp(f"第 {_} 次 HTTP请求失败，给'子节点'企业发送删除通知确认失败！错误代码:{e}")
            print_with_timestamp(f"系统尝试发送 {max_retries} 次后，仍未发送成功！")
            return None
        else:
            # 标识本企业就是根节点，直接进行数据存储
            print_with_timestamp(f"本企业{Bus_id}对于本条信息的'父节点'为{node},开始进行完整信息存证！")
            return True


