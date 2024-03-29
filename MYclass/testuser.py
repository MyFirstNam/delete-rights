import requests
from flask import json

if __name__ == "__main__":
    delintention = {
        "affairs_id": "dengxin",
        "user_id": "dengxin",
        "deleteGranularity": "dengxin",
        "info_id": "dengxin",
        "source_bus_id": "dengxin",
        "count_limit": "dengxin",
        "deleteMethod": "dengxin"
    }
    delintention = json.dumps(delintention)
    ip = "127.0.0.1"  # 源企业节点开放的ip
    port = 20000
    url = f"http://{ip}:{port}/your/post/endpoint"  # 替换为自己的实际目标URL
    response = requests.post(url, json=delintention)
    # 检查响应
    if response.status_code == 200:
        print("POST请求成功")
        print(response.text)
    else:
        print("POST请求失败")
        print("响应状态码:", response.status_code)

    ip = "127.0.0.1"  # 源企业节点开放的ip
    port = 20000
    url = f"http://{ip}:{port}/confirm/postx/endpointx"  # 替换为自己的实际目标URL
    response = requests.post(url, json=delintention)
    # 检查响应
    if response.status_code == 200:
        print("POST请求成功")
        print(response.text)
    else:
        print("POST请求失败")
        print("响应状态码:", response.status_code)


    delintention = {
        "affairs_id": "dengxin",
        "user_id": "dengxin",
        "deleteGranularity": "dengxin",
        "info_id": "dengxin",
        "source_bus_id": "dengxin",
        "count_limit": "dengxin",
        "deleteMethod": "dengxin"
    }
    delintention = json.dumps(delintention)
    ip = "127.0.0.1"  # 源企业节点开放的ip
    port = 20000
    url = f"http://{ip}:{port}/your/post/endpoint"  # 替换为自己的实际目标URL
    response = requests.post(url, json=delintention)
    # 检查响应
    if response.status_code == 200:
        print("POST请求成功")
        print(response.text)
    else:
        print("POST请求失败")
        print("响应状态码:", response.status_code)




    delNotice = {
        "affairs_id": "000001",
        "user_id": "0x000001",
        "info_id": "12134231313",
        "from_bus_id": "b0001",
        "to_bus_id": "b0002",  # 实现过程中，此参数应该是一个字符串，表示后续发送给某一个节点，在生成删除通知时需要根据情况更新
        "deleteMethod": "age",
        "deleteGranularity": "软件删除",
        "deleteNotifyTree": "12321323211321"  # 一个JSON
    }

    delNotice = json.dumps(delNotice)
    ip = "127.0.0.1"  # 源企业节点开放的ip
    port = 20001
    url = f"http://{ip}:{port}/test/postx/endpointx"  # 替换为自己的实际目标URL
    response = requests.post(url, json=delintention)
    # 检查响应
    if response.status_code == 200:
        print("POST请求成功")
        print(response.text)
    else:
        print("POST请求失败")
        print("响应状态码:", response.status_code)


{
    'affairs_id': '0001',
    'user_id': 'b00002',
    'info_id': '0x0002',
    'from_bus_id': 'b1000',
    'to_bus_id': 'b1001',
    'deleteMethod': '软件删除',
    'deleteGranularity': 'age',
    'deleteNotifyTree': '{"b1000": {"children": [{"b1001": {"children": ["b1002"]}}, {"b1003": {"children": ["b1004"]}}]}}'
}