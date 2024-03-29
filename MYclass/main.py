# main.py
from log_request import send_log_request, load_config, find_system_ips
from database_utils import connect_to_database, create_table_if_not_exists, record_exists, process_json_file
from trigger_correctness_verification import TriCorVerification
from evaluation_notification import NotificationTreeUtils, EvaluationResultCollector, receive_evaluation, load_config2, \
    find_node_id_by_ip, get_notification_data, get_verification_result, parse_notification_tree, start_flask_app, \
    fetch_notification_pairs, send_evaluation_notifications, send_evaluation_notification

from rootdeleteTriCorVern import TriCorVerification
from rootdeleteNotConComAnas import ComAnalysis
from rootdeleteConEvaRet import generate_delete_level, ConEvaluation
from rootdeleteMetComEvan import ComEvaluation
from rootdeleteDupNonrecAsst import DupNonrecAsst
from rootdeleteDupComVern import RetentionStatusClient, DeleteDupComVern, fetch_unique_id_pairs, process_each_pair
from rootdeleteOpeCorVern import CombinedClient, CombinedEvaluator, fetch2_unique_id_pairs, process2_each_pair
from rootdeleteEffectEvaRet import DeleteEffectEvaluator
from evaluation_notification import app
import threading
import json
import requests
import mysql.connector
from mysql.connector import Error
import json
import requests
import mysql.connector
from mysql.connector import Error
from flask import Flask, request, jsonify
import threading
import json
import os
import requests
import mysql.connector
from mysql.connector import Error
import json

# 日志文件名
LOG_TYPES = ['Delete_Intent', 'Delete_Request', 'Delete_Trigger', 'Delete_Notification', 'Delete_Confirmation',
             'Delete_Operation']

# 数据库连接参数
DB_HOST = '127.0.0.1'
DB_USER = 'aaa'
DB_PASSWORD = '123456'
DB_DATABASE = 'abc'

from flask import Flask, request, jsonify
import threading

app = Flask(__name__)

# def start_flask_app():
#     app.run(host='0.0.0.0', port=5000)

# # 启动 Flask 应用接收评测结果
# threading.Thread(target=start_flask_app).start()

# 新的路由用于接收其他节点发来的信息
# @app.route('/receive-node-info', methods=['POST'])
# def receive_node_info():
#     try:
#         data = request.json  # 获取 JSON 数据
#         # 在这里处理收到的信息，可以根据需要进行其他操作
#         print("Received node information:", data)
#         return jsonify({"status": "success", "message": "NodeSimulation information received successfully"})
#     except Exception as e:
#         print(f"Error processing node information: {e}")
#         return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == "__main__":

    config = load_config('config3.json')
    my_ip = input("请输入您的系统IP地址：")

    delete_notification_ip, deterministic_delete_ip = find_system_ips(config, my_ip)
    if not delete_notification_ip or not deterministic_delete_ip:
        print("未找到对应的系统IP地址")

    server_log_mapping = {
        "Delete_Intent": f'http://{delete_notification_ip}:5000/getIntentLog',
        "Delete_Request": f'http://{delete_notification_ip}:5000/getRequestLog',
        "Delete_Trigger": f'http://{delete_notification_ip}:5000/getTriggerLog',
        "Delete_Notification": f'http://{delete_notification_ip}:5000/getNotificationLog',
        "Delete_Confirmation": f'http://{delete_notification_ip}:5000/getConfirmationLog',
        "Delete_Operation": f'http://{deterministic_delete_ip}:5000/getOperationLog',
    }
    # 日志请求
    # 用户选择请求类型
    choice = input("请选择请求类型（1: 时间段, 2: infoID）：")
    infoID, time = None, None
    if choice == '1':
        start_time = input("请输入开始时间：")
        end_time = input("请输入结束时间：")
        time = f"{start_time} to {end_time}"
    elif choice == '2':
        infoID = input("请输入infoID：")
    else:
        print("无效的选择")

    # 发送所有类型的日志请求
    for log_type, server_url in server_log_mapping.items():
        send_log_request(server_url, log_type, infoID, time)

    # 连接数据库
    db_connection = connect_to_database()
    # if db_connection is None:
    cursor = db_connection.cursor()
    # cursor = connection.cursor(dictionary=True)

    # 创建日志类型对应的表
    for log_type in LOG_TYPES:
        create_table_if_not_exists(cursor, log_type)

    # def process_log_files(cursor, directory, log_types):
    # file_list = os.listdir(directory)
    # filtered_file_list = [file for file in file_list if any(log_type in file for log_type in log_types)]
    # for file in filtered_file_list:
    #    process_json_file(cursor, os.path.join(directory, file))

    # process_log_files(cursor, "path_to_log_files", LOG_TYPES)
    # 处理日志文件并插入到数据库
    local_files_directory = os.path.join("C:\\Users", "xu", "Documents", "GitHub", "1.6", "log")
    file_list = os.listdir(local_files_directory)
    filtered_file_list = [file for file in file_list if any(log_type in file for log_type in LOG_TYPES)]

    for file in filtered_file_list:
        process_json_file(cursor, os.path.join(local_files_directory, file))

    #########################删除触发正确性验证#########################
    # 触发正确性验证
    cursor = db_connection.cursor()
    tricor_verification = TriCorVerification(cursor)
    tricor_verification.perform_verification()
    db_connection.commit()
    # tricor_verification = TriCorVerification(cursor)
    # tricor_verification.perform_verification()

    # perform_verification()
    # perform_verification(cursor)

    #########################删除通知与确认完备性分析#########################
    db_connection = mysql.connector.connect(
        host='127.0.0.1', user='aaa', password='123456', database='abc'
    )
    cursor = db_connection.cursor()
    com_analysis = ComAnalysis(cursor)
    com_analysis.perform_verification()
    db_connection.commit()

    #########################删除一致性评测#########################
    db_connection = mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_DATABASE)
    cursor = db_connection.cursor()
    con_evaluation = ConEvaluation(cursor)
    con_evaluation.perform_evaluation()
    db_connection.commit()

    #########################删除方法合规评测#########################

    db_connection = mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_DATABASE)
    cursor = db_connection.cursor()

    com_evaluation = ComEvaluation(cursor)
    com_evaluation.create_eval_result_table_if_not_exists()
    com_evaluation.calculate_compliance()

    db_connection.commit()

    #########################删除副本的不可恢复性评估#########################

    db_connection = mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_DATABASE)
    cursor = db_connection.cursor()

    dup_nonrec_asst = DupNonrecAsst(cursor)
    dup_nonrec_asst.perform_evaluation()

    db_connection.commit()

    #########################多副本删除完备性验证#########################

    id_pairs = fetch_unique_id_pairs()
    for info_id, affairs_id in id_pairs:
        # print(f"Processing pair: info_id={info_id}, affairs_id={affairs_id}")
        retention_client = RetentionStatusClient(info_id, affairs_id)
        response_file = retention_client.run()
        if response_file:
            process_each_pair(info_id, affairs_id)
        # else:
        #     return 0#print(f"No response file for info_id={info_id}, affairs_id={affairs_id}")

    #########################删除操作正确性验证#########################
    id_pairs = fetch2_unique_id_pairs()
    for info_id, affairs_id in id_pairs:
        # print(f"Processing pair: info_id={info_id}, affairs_id={affairs_id}")
        retention_client = CombinedClient(info_id, affairs_id)
        result = retention_client.run()
        if result["success"]:
            process2_each_pair(info_id, affairs_id)
            # 处理其他逻辑
        # else:
        #     return 0#print(f"Error: {result['error_message']}")

    #########################删除评测结果汇总#########################
    # deleteEffectEvaRet整体删除效果评估结果
    evaluator = DeleteEffectEvaluator('127.0.0.1', 'aaa', '123456', 'abc')
    evaluator.run_evaluation()
    # db_conn = connect_to_database()
    # if db_conn is not None:
    #     cursor = db_conn.cursor()
    #     create_eval_result_table_if_not_exists(cursor)
    #     update_delete_effect_eva_ret(cursor)

    #     db_conn.commit()

    # 启动 Flask 应用接收评测结果
    # threading.Thread(target=start_flask_app).start()

    # 发送评测通知
    # 评测通知和结果收集
    cursor = db_connection.cursor(dictionary=True)
    config2 = load_config2('config2.json')
    my_node_id = find_node_id_by_ip(my_ip, config2)
    # if my_node_id:
    #     threading.Thread(target=start_flask_app).start()
    #     send_evaluation_notifications(my_node_id, cursor, config, DB_HOST, DB_USER, DB_PASSWORD, DB_DATABASE)
    if my_node_id:
        send_evaluation_notifications(my_node_id, my_ip, cursor, config2)
    # cursor = db_connection.cursor()
    # # 关闭数据库连接
    # cursor.close()
    # db_connection.close()

    app.run(host='0.0.0.0', port=5000)
# if __name__ == "__main__":
#     #app.run(port=5000, debug=True)
#     main()
#     app.run(port=5000, debug=True)
#     # 启动 Flask 应用
#       # 确保从正确的文件导入 Flask 应用


# def process_log_files(cursor, directory, log_types):
#     file_list = os.listdir(directory)
#     filtered_file_list = [file for file in file_list if any(log_type in file for log_type in log_types)]
#     for file in filtered_file_list:
#         process_json_file(cursor, os.path.join(directory, file))


# def send_evaluation_notifications(my_node_id, cursor, config, db_host, db_user, db_password, db_database):
#     try:
#         # 连接数据库
#         connection = mysql.connector.connect(host=db_host, user=db_user, password=db_password, database=db_database)
#         cursor = connection.cursor(dictionary=True)

#         # 查询需要发送通知的数据
#         cursor.execute("SELECT DISTINCT `infoID`, `affairsID` FROM `delete_Notification_logs_table`")
#         pairs = cursor.fetchall()
#         print("Starting notification process...")
#         # 开始发送通知的过程
#         for pair in pairs:
#             info_id, affairs_id = pair['infoID'], pair['affairsID']
#             # 获取验证结果
#             result = get_verification_result(cursor, info_id, affairs_id)

#             # 验证通过后，处理通知
#             if result == 1:
#                 notification_data = get_notification_data(cursor, info_id, affairs_id)
#                 for data in notification_data:
#                     # 解析通知树
#                     intermediate = json.loads(data['deleteNotifyTree'])
#                     json_tree = json.loads(intermediate)

#                     # 查找除当前节点外的所有节点
#                     nodes_to_notify = NotificationTreeUtils.find_all_nodes_except(json_tree, my_node_id)

#                     # 向每个节点发送评测通知
#                     for node_id in nodes_to_notify:
#                         node = next((n for n in config['nodes'] if n['system_id'] == node_id), None)
#                         if node:
#                             send_evaluation_notification(node, data)
#             else:
#                 print(f"Skipping infoID {info_id}, affairsID {affairs_id} due to failed verification")

# except Error as e:
#     print(f"Database error: {e}")
# finally:
#     if connection and connection.is_connected():
#         cursor.close()
#         connection.close()








