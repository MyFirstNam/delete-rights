# import asyncio
#
# import requests
# from flask import Flask, json, jsonify
# from flask import Blueprint
# from test2 import app2
# import threading
#
# app1 = Blueprint("app1", __name__)
# app = Flask(__name__)
#
# async def handle_request_from_user():
#     await asyncio.sleep(2)  # 模拟处理用户请求的耗时操作
#     response = "test1收到用户请求"
#     return jsonify({"response": response})
#
# async def perform_business_operation():
#     await asyncio.sleep(2)  # 模拟业务操作的耗时操作
#     print("test1执行业务操作")
#     delintention = {
#         "affairs_id": "dengxin",
#         "user_id": "dengxin",
#         "deleteGranularity": "dengxin",
#         "info_id": "dengxin",
#         "source_bus_id": "dengxin",
#         "count_limit": "dengxin",
#         "deleteMethod": "dengxin"
#     }
#     print(delintention)
#
# @app1.route('/test1', methods=['POST'])
# async def page2():
#     user_task = asyncio.create_task(handle_request_from_user())
#     business_task = asyncio.create_task(perform_business_operation())
#
#     # 首先响应用户请求
#     user_response = await user_task
#
#     # 然后执行后续业务操作
#     await business_task
#
#     return user_response
#
# if __name__ == '__main__':
#     app.register_blueprint(app2)
#     app.register_blueprint(app1)
#     app.run(host='0.0.0.0', port=50000)
# import pymysql
# from InfoMemory import InfoMemory
# import socket
# # 设置数据库连接参数
# db_params = {
#     'host': socket.gethostbyname(socket.gethostname()),
#     'user': 'myuser',
#     'password': 'mypassword',
#     'database': 'project26',
#     'port': 3306,
# }
#
# try:
#     # 连接到数据库
#     connection = pymysql.connect(**db_params)
#
#     # 创建一个游标对象，用于执行SQL查询
#     cursor = connection.cursor()
#
#     # 执行SQL查询
#     cursor.execute("SELECT * FROM `b00001`")
#
#     # 检索查询结果
#     records = cursor.fetchall()
#     for record in records:
#         print(record)
#
#     # 关闭游标和数据库连接
#     cursor.close()
#     connection.close()
#
# except (pymysql.MySQLError) as error:
#     print("数据库连接或查询时发生错误:", error)

# if __name__ == '__main__':
#     processor = InfoMemory(host="10.170.42.45", port=3306, user="myuser", password="mypassword", database="project26")

# import hmac
# import hashlib
# import json

# def generate_hmac(message, key):
#     # 使用 SHA-256 作为哈希函数
#     hash_function = hashlib.sha256
#
#     # 使用 hmac.new() 函数创建一个 HMAC 对象，传入密钥和消息
#     hmac_object = hmac.new(key.encode(), message.encode(), hash_function)
#
#     # 获取消息认证码
#     hmac_code = hmac_object.digest()
#
#     return hmac_code
#
#
# def verify_hmac(message, key, received_hmac):
#     # 生成接收到的消息的期望消息认证码
#     expected_hmac = generate_hmac(message, key)
#
#     # 使用 hmac.compare_digest() 来比较期望的消息认证码和接收到的消息认证码
#     if hmac.compare_digest(expected_hmac, received_hmac):
#         return True
#     else:
#         return False
#
#
# # 示例用法
# delNotice = {
#     "affairs_id":"affairs_id",
#     "user_id":"user_id",
#     "info_id":"info_id",
#     "from_bus_id": "Bus_id",
#     "to_bus_id": "",
#     "deleteMethod": "deleteMethod",
#     "deleteGranularity":"deleteGranularity",
#     "deleteNotifyTree": "deleteNotifyTree"  # 一个字典
# }
# secret_key = "my_secret_key"
# message_to_send = json.dumps(delNotice)
# # 生成消息认证码
# hmac_code = generate_hmac(message_to_send, secret_key)
# print("Generated HMAC:", hmac_code.hex())
#
# # 模拟接收方验证消息认证码
# is_valid = verify_hmac(message_to_send, secret_key, hmac_code)
# print("Is valid:", is_valid)


# import mysql.connector
#
# # 连接 MySQL 服务器
# connection = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     password="123456"
# )
#
# # 创建一个游标对象
# cursor = connection.cursor()
# # # processor = InfoMemory(host="localhost", user="root", port=3306, password="123456", database="project26")
# # # processor = InfoMemory(host="10.170.42.45", port=3306, user="myuser", password="mypassword", database="project26")
# # # processor.insert_record(delNotice["user_id"], delNotice["info_id"],delNotice["deleteMethod"],delNotice["deleteGranularity"],delNotice["deleteNotifyTree"],triggerType,Bus_id,Timememory,Countmemory)
# # 新建数据库的 SQL 语句
# database_name = "test_mysql"
# create_database_query = f"CREATE DATABASE {database_name}"
#
# # 执行 SQL 语句
# cursor.execute(create_database_query)
#
# # 关闭游标和连接
# cursor.close()
# connection.close()


#
# import mysql.connector
#
# def is_database_exists(host, user, password, database):
#     try:
#         connection = mysql.connector.connect(
#             host=host,
#             user=user,
#             password=password,
#             database=database
#         )
#         return True
#     except mysql.connector.Error as err:
#         return False
#     finally:
#         if 'connection' in locals() and connection.is_connected():
#             connection.close()
#
# # 示例用法
# host= "localhost"
# user= "root"
# password="123456"
# database = "test_mysql"
# if is_database_exists(host, user, password, database):
#     print("数据库存在")
# else:
#     print("数据库不存在")
#


from threading import Thread
from time import sleep
import requests
from flask import Flask, request
from celery import Celery
import asyncio

app = Flask(__name__)

@app.route('/do_something', methods=['POST'])
def do_something():
    def background_task():
        # 这里执行长时间运行的操作
        sleep(30)

        url = f"http://127.0.0.1:10000/do_something"
        # 要发送的数据
        data = {
            "key1": "value1",
            "key2": "value2",
            'need_timing': "100"
        }

        # 发送 POST 请求
        response = requests.post(url, json=data)

        # 打印响应内容
        print("Status Code:", response.status_code)
        print("Response Body:", response.text)

        print("计时线程测试成功!")


    # background_task()
    thread = Thread(target=background_task)
    thread.start()
    print("测试没有问题")
    return 'Started a background task.'


@app.route('/do_something1', methods=['POST'])
def do_something1():
    def background_task():
        # 这里执行长时间运行的操作
        sleep(20)
        print("111111测试成功!")

    # background_task()
    thread = Thread(target=background_task)
    thread.start()
    print("111111111测试没有问题")
    return '111111Started a background task.'


@app.route('/do_something2', methods=['POST'])
def do_something2():
    def background_task():
        # 这里执行长时间运行的操作
        sleep(10)
        print("222222测试成功!")

    # background_task()
    thread = Thread(target=background_task)
    thread.start()
    print("222222测试没有问题")
    return '2222222Started a background task.'

# app.config['CELERY_BROKER_URL'] = 'redis://127.0.0.1:6379/0'
# app.config['CELERY_RESULT_BACKEND'] = 'redis://127.0.0.1:6379/0'
#
# celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
# celery.conf.update(app.config)
#
#
# @celery.task
# def process_data(data):
#     # 处理数据的代码
#    # sleep(10)
#     print("接收到数据")
#     ...
#
# @app.route('/do_something', methods=['POST'])
# def process():
#     data = request.get_json()  # 假设数据以 JSON 形式发送
#     process_data.delay(data)  # 发送任务到 Celery
#     return 'Task submitted to Celery', 202



# async def handle_timed_packet(data):
#     # 设置计时时间，例如5秒
#     await asyncio.sleep(20)
#     # 计时结束后处理数据
#     print("处理计时数据包: ", data)
#
# @app.route('/process_packet', methods=['POST'])
# def process_packet():
#     data = request.get_json()
#     if data['need_timing']:
#         # 如果需要计时，启动一个异步任务来处理
#         asyncio.create_task(handle_timed_packet(data))
#     else:
#         # 不需要计时，直接处理
#         print("处理普通数据包: ", data)
#     return "数据包已接收"


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=10000, debug=True)
