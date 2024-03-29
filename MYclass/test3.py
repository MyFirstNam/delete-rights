import json

import requests

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
    "time_limit": "10",  # 时间限制为可选字段，不是每次内容都有，”“空字符表示没有时间显示
    "count_limit": 0,  # 次数限制为可选字段，不是每次内容都有,0表示没有次数限制
    "deleteMethod": "硬件删除"
}
data = json.dumps(data)
# 发送 POST 请求
response = requests.post(url, json=data)

# 打印响应内容
print("Status Code:", response.status_code)
print("Response Body:", response.text)

# import logging
#
# # 配置日志记录
# logging.basicConfig( level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
#
# # 记录日志
# # logging.debug('这是一个调试信息')
# # logging.info('这是一个信息')
# # logging.warning('这是一个警告')
# # logging.error('这是一个错误')
# # logging.critical('这是一个严重错误')
#
#
# delintention = {
#     "affairs_id": "00001",
#     "user_id": "u00001",
#     "deleteGranularity": "age",
#     "info_id": "a1b2c3d4e5",
#     "source_bus_id": "b00001",
#     "time_limit": "yyyy",  # 时间限制为可选字段，不是每次内容都有，""空字符表示没有时间显示
#     "count_limit": 9,  # 次数限制为可选字段，不是每次内容都有,0表示没有次数限制
#     "deleteMethod": "硬件删除"
# }
#
# 时间限制不为空，次数限制为空
# 计时触发（自动触发之一）
# if delintention["time_limit"] and delintention["count_limit"] == 0:
#     logging.info("计时触发")
# # 计次触发（自动触发之一）
# elif not delintention["time_limit"] and delintention["count_limit"] != 0:
#     logging.info("计次触发")
#
# # 按需触发
# elif not delintention["time_limit"] and delintention["count_limit"] == 0:
#     logging.info("按需触发")
#
# # 输入格式不规范，无法解析
# else:
#     logging.error("格式不规范触发")


# import threading
#
#
# def tst():
#     def timer_action():
#         print("计时触发成功")
#
#     # 设置计时器，10秒后执行 timer_action 函数
#     timer = threading.Timer(10, timer_action)
#     print("开始计时")
#     # 启动计时器
#     timer.start()
#
# tst()