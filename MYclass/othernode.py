from flask import Flask, request, jsonify
import json
import requests
import socket
import mysql.connector
from mysql.connector import Error
from rootdeleteNotConComAnas import ComAnalysis
import threading
from otherdatabase import connect_to_database, create_table_if_not_exists, record_exists, process_json_file
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

from otherdeleteNotConComAnas import ComAnalysis
from otherdeleteConEvaRet import generate_delete_level, ConEvaluation
from otherdeleteMetComEvan import ComEvaluation
from otherdeleteDupNonrecAsst import DupNonrecAsst
from otherdeleteDupComVern import RetentionStatusClient, DeleteDupComVern, fetch_unique_id_pairs, process_each_pair
from otherdeleteOpeCorVern import CombinedClient, CombinedEvaluator, fetch2_unique_id_pairs, process2_each_pair
from otherdeleteEffectEvaRet import DeleteEffectEvaluator
from evaluation_notification import app
# 日志文件名
LOG_TYPES = ['Delete_Confirmation', 'Delete_Operation']


#########################根节点其他节点#########################
class NotificationTreeUtils:
    @staticmethod
    def find_all_nodes_except(json_tree, exclude_node, current_node=None, result=None):
        """
        查找除了指定节点外的所有其他节点。
        
        :param json_tree: 传播树的 JSON 对象。
        :param exclude_node: 要排除的节点。
        :param current_node: 当前遍历的节点。
        :param result: 用于存储结果的列表。
        :return: 所有除了指定节点外的其他节点的列表。
        """
        if result is None:
            result = []
        if current_node is None:
            current_node = list(json_tree.keys())[0]

        if current_node != exclude_node:
            result.append(current_node)

        children = json_tree.get(current_node, {}).get('children', [])
        for child in children:
            if isinstance(child, dict):
                for key in child.keys():
                    NotificationTreeUtils.find_all_nodes_except(child, exclude_node, key, result)
            elif child != exclude_node:
                result.append(child)

        return result

    @staticmethod
    def find_parent(json_tree, target_node, current_node=None, parent=None):
        """
        查找给定节点的父节点。
        
        :param json_tree: 传播树的 JSON 对象。
        :param target_node: 要查找父节点的目标节点。
        :param current_node: 当前遍历的节点。
        :param parent: 当前节点的父节点。
        :return: 目标节点的父节点。
        """
        # 如果是树的第一层，设置当前节点为根节点
        if current_node is None:
            current_node = list(json_tree.keys())[0]

        # 如果找到目标节点，返回父节点
        if current_node == target_node:
            return parent

        # 如果当前节点有子节点，递归遍历子节点
        children = json_tree.get(current_node, {}).get('children', [])
        for child in children:
            if isinstance(child, dict):
                # 子节点也是一个字典（有自己的子节点）
                for key in child.keys():
                    found_parent = NotificationTreeUtils.find_parent(child, target_node, key, current_node)
                    if found_parent is not None:
                        return found_parent
            elif child == target_node:
                # 直接找到目标节点
                return current_node

        return None

    @staticmethod
    def get_root_node(json_tree):
        return list(json_tree.keys())[0]
    



app = Flask(__name__)

def load_config(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def send_log_request(server_url, log_type, infoID, affairsID):
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    payload = {
        "systemID": 1,
        "systemIP": "210.73.60.100",
        "mainCMD": 1,
        "subCMD": 32,
        "evidenceID": "00032dab40af0c56d2fa332a4924d150",
        "msgVersion": 4096,
        "submittime": "2023-11-08 00:15:28",
        "data": {
            "infoID": infoID,
            "affairsID": affairsID,
            "getLogType": f"get{log_type}Log"
        },
        "dataHash": "56e3be093f377b9d984eef02a982d852d1bce062fdb505bcf87df46141fd80aa",
        "datasign": "56e3be093f377b9d984eef02a982d852d1bce062fdb505bcf87df46141fd80aa"
    }

    response = requests.post(server_url, json=payload, headers=headers)

    if response.status_code == 200:
        try:
            response_data = response.json()
            file_name = f"{log_type}_{infoID}_{affairsID}_log.json" # 文件名现在只基于日志类型
            with open(file_name, 'w') as file:
                json.dump(response_data, file, indent=4)
            print(f"File saved: {file_name}")
        except json.JSONDecodeError:
            print(f"Error: Unable to parse JSON response from {server_url}")
    else:
        print(f"Error: Request to {server_url} failed with status code {response.status_code}")

    # 打印响应状态码和内容
    print(f"Response from {server_url}:")
    print("Status Code:", response.status_code)
    print("Response Content:", response.content)
    # return response  # 也可以选择返回响应对象以进行进一步处理


def save_log(data, log_type, infoID, affairsID):
    file_name = f"{log_type}_{infoID}_{affairsID}_log.json"
    with open(file_name, 'w') as file:
        json.dump(data, file, indent=4)
    return file_name

def compare_logs(file1, file2):
    try:
        with open(file1, 'r') as f1, open(file2, 'r') as f2:
            return json.load(f1) == json.load(f2)
    except Exception as e:
        print(f"Error comparing files: {e}")
        return False


# 处理日志数据!!!!!!!!
def process_log_data(data, infoID, affairsID):
    # 处理日志数据
    root_notification_file = save_log(data, 'RootNotification', infoID, affairsID)
    delete_notification_file = f"Delete_Notification_{infoID}_{affairsID}_log.json"
    status_message, status_code = process_and_insert_log(delete_notification_file)
    return status_message, status_code

def compare_notification_logs(cursor, data, infoID, affairsID):
    # 比较通知日志
    match, message = compare_notification_with_db(cursor, data, infoID, affairsID)
    return match, message


# 数据库连接配置
DB_HOST = '127.0.0.1'
DB_USER = 'aa'
DB_PASSWORD = '123456'
DB_DATABASE = 'ab'

# 数据库连接函数
def connect_to_database():
    try:
        return mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_DATABASE)
    except mysql.connector.Error as e:
        app.logger.error(f"Error connecting to MySQL database: {e}")
        return None

def create_table_for_confirmation_and_operation_logs(cursor):
    create_confirmation_log_table_query = '''
    CREATE TABLE IF NOT EXISTS `delete_confirmation_logs_table` (
        `userID` VARCHAR(100) DEFAULT NULL,
        `infoID` VARCHAR(100) NOT NULL,
        `affairsID` VARCHAR(100) NOT NULL,
        `deleteMethod` VARCHAR(100) DEFAULT NULL,
        `deleteGranularity` VARCHAR(100) DEFAULT NULL,
        `sourceDomainID` VARCHAR(100) DEFAULT NULL,
        `timeLimit` VARCHAR(100) DEFAULT NULL,
        `countLimit` VARCHAR(100) DEFAULT NULL,
        `deletePerformer` VARCHAR(100) DEFAULT NULL,
        `deletePerformTime` VARCHAR(100) DEFAULT NULL,
        `deleteDupinfoID` JSON DEFAULT NULL,
        `deleteInstruction` JSON DEFAULT NULL,
        `deleteControlSet` JSON DEFAULT NULL,
        `deleteAlg` INT DEFAULT NULL,
        `deleteAlgParam` VARCHAR(100) DEFAULT NULL,
        `deleteLevel` INT DEFAULT NULL,
        `abstract` TEXT DEFAULT NULL,
        `category` VARCHAR(100) DEFAULT NULL,
        `keyWords` VARCHAR(100) DEFAULT NULL,
        `title` TEXT DEFAULT NULL,
        `delConfirmSignatureDict` JSON DEFAULT NULL,
        `deleteConfirmation` VARCHAR(100) DEFAULT NULL,
        `deleteNotifyTree` JSON DEFAULT NULL,
        `classification_info` JSON DEFAULT NULL,
        `deleteIntention` TEXT DEFAULT NULL,
        `infoType` INT DEFAULT NULL,
        `deleteKeyinfoID` JSON DEFAULT NULL,
        PRIMARY KEY (`infoID`, `affairsID`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    '''
    cursor.execute(create_confirmation_log_table_query)

    create_operation_log_table_query = '''
    CREATE TABLE IF NOT EXISTS `delete_operation_logs_table`(
        `userID` VARCHAR(100) DEFAULT NULL,
        `infoID` VARCHAR(100) NOT NULL,
        `affairsID` VARCHAR(100) NOT NULL,
        `deleteMethod` VARCHAR(100) DEFAULT NULL,
        `deleteGranularity` VARCHAR(100) DEFAULT NULL,
        `sourceDomainID` VARCHAR(100) DEFAULT NULL,
        `timeLimit` VARCHAR(100) DEFAULT NULL,
        `countLimit` VARCHAR(100) DEFAULT NULL,
        `deletePerformer` VARCHAR(100) DEFAULT NULL,
        `deletePerformTime` VARCHAR(100) DEFAULT NULL,
        `deleteDupinfoID` JSON DEFAULT NULL,
        `deleteInstruction` JSON DEFAULT NULL,
        `deleteControlSet` JSON DEFAULT NULL,
        `deleteAlg` INT DEFAULT NULL,
        `deleteAlgParam` VARCHAR(100) DEFAULT NULL,
        `deleteLevel` INT DEFAULT NULL,
        `abstract` TEXT DEFAULT NULL,
        `category` VARCHAR(100) DEFAULT NULL,
        `keyWords` VARCHAR(100) DEFAULT NULL,
        `title` TEXT DEFAULT NULL,
        `delConfirmSignatureDict` JSON DEFAULT NULL,
        `deleteConfirmation` VARCHAR(100) DEFAULT NULL,
        `deleteNotifyTree` JSON DEFAULT NULL,
        `classification_info` JSON DEFAULT NULL,
        `deleteIntention` TEXT DEFAULT NULL,
        `infoType` INT DEFAULT NULL,
        `deleteKeyinfoID` JSON DEFAULT NULL,
        PRIMARY KEY (`infoID`, `affairsID`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    '''
    cursor.execute(create_operation_log_table_query)

# 创建日志表
def create_table_if_not_exists(cursor):
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS `Delete_Notification_logs_table` (
        `userID` VARCHAR(100) DEFAULT NULL,
        `infoID` VARCHAR(100) NOT NULL,
        `affairsID` VARCHAR(100) NOT NULL,
        `deleteMethod` VARCHAR(100) DEFAULT NULL,
        `deleteGranularity` VARCHAR(100) DEFAULT NULL,
        `sourceDomainID` VARCHAR(100) DEFAULT NULL,
        `timeLimit` VARCHAR(100) DEFAULT NULL,
        `countLimit` VARCHAR(100) DEFAULT NULL,
        `deletePerformer` VARCHAR(100) DEFAULT NULL,
        `deletePerformTime` VARCHAR(100) DEFAULT NULL,
        `deleteDupinfoID` JSON DEFAULT NULL,
        `deleteInstruction` JSON DEFAULT NULL,
        `deleteControlSet` JSON DEFAULT NULL,
        `deleteAlg` INT DEFAULT NULL,
        `deleteAlgParam` VARCHAR(100) DEFAULT NULL,
        `deleteLevel` INT DEFAULT NULL,
        `abstract` TEXT DEFAULT NULL,
        `category` VARCHAR(100) DEFAULT NULL,
        `keyWords` VARCHAR(100) DEFAULT NULL,
        `title` TEXT DEFAULT NULL,
        `delConfirmSignatureDict` JSON DEFAULT NULL,
        `deleteConfirmation` VARCHAR(100) DEFAULT NULL,
        `deleteNotifyTree` JSON DEFAULT NULL,
        `classification_info` JSON DEFAULT NULL,
        `deleteIntention` TEXT DEFAULT NULL,
        `infoType` INT DEFAULT NULL,
        `deleteKeyinfoID` JSON DEFAULT NULL,
        PRIMARY KEY (`infoID`, `affairsID`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    '''
    cursor.execute(create_table_query)

def insert_log_record(cursor, log_data):
    # 确保 log_data 是一个列表
    if not isinstance(log_data, list):
        log_data = [log_data]

    for record in log_data:
        # 提取 'data' 字典
        data = record.get('data')
        if not isinstance(data, dict):
            print(f"Invalid data format in record: {record}")
            continue

        # 提取 'data' 字典中的各个字段
        user_id = data.get('userID')
        info_id = data.get('infoID')
        affairs_id = data.get('affairsID')
        delete_method = data.get('deleteMethod')
        delete_granularity = data.get('deleteGranularity')
        delete_notify_tree_json = json.dumps(data.get('deleteNotifyTree', {}))

        # 构建和执行SQL插入语句
        insert_query = '''
            INSERT INTO `Delete_Notification_logs_table` (
                `userID`, `infoID`, `affairsID`, `deleteMethod`, `deleteGranularity`, 
                `deleteNotifyTree`
            ) VALUES (
                %(userID)s, %(infoID)s, %(affairsID)s, %(deleteMethod)s, %(deleteGranularity)s, 
                %(deleteNotifyTree)s
            ) ON DUPLICATE KEY UPDATE
                `deleteMethod` = %(deleteMethod)s, `deleteGranularity` = %(deleteGranularity)s, 
                `deleteNotifyTree` = %(deleteNotifyTree)s
        '''

        insert_params = {
            'userID': user_id,
            'infoID': info_id,
            'affairsID': affairs_id,
            'deleteMethod': delete_method,
            'deleteGranularity': delete_granularity,
            'deleteNotifyTree': delete_notify_tree_json
        }

        cursor.execute(insert_query, insert_params)



# def insert_log_record(cursor, log_data):
#     # 确保 log_data 是一个列表
#     if not isinstance(log_data, list):
#         log_data = [log_data]

#     for record in log_data:
#         # 提取 'data' 字典
#         data = record.get('data')
#         if not isinstance(data, dict):
#             print(f"Invalid data format in record: {record}")
#             continue

#         # 提取 'data' 字典中的各个字段
#         user_id = data.get('userID')
#         info_id = data.get('infoID')
#         affairs_id = data.get('affairsID')
#         delete_method = data.get('deleteMethod')
#         delete_granularity = data.get('deleteGranularity')
#         delete_notify_tree_json = json.dumps(data.get('deleteNotifyTree', {}))

#         # 构建和执行SQL插入语句
#         insert_query = '''
#             INSERT INTO `Delete_Notification_logs_table` (
#                 `userID`, `infoID`, `affairsID`, `deleteMethod`, `deleteGranularity`, 
#                 `deleteNotifyTree`
#             ) VALUES (
#                 %(userID)s, %(infoID)s, %(affairsID)s, %(deleteMethod)s, %(deleteGranularity)s, 
#                 %(deleteNotifyTree)s
#             )
#         '''

#         insert_params = {
#             'userID': user_id,
#             'infoID': info_id,
#             'affairsID': affairs_id,
#             'deleteMethod': delete_method,
#             'deleteGranularity': delete_granularity,
#             'deleteNotifyTree': delete_notify_tree_json
#         }

#         cursor.execute(insert_query, insert_params)



# 读取并处理日志文件
def process_and_insert_log(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        log_data = json.load(file)

    db_conn = connect_to_database()
    if db_conn is None:
        return "Database connection failed", 500

    cursor = db_conn.cursor()
    create_table_if_not_exists(cursor)

    try:
        # 如果 log_data 是一个列表，则迭代插入每个条目
        if isinstance(log_data, list):
            for data_entry in log_data:
                insert_log_record(cursor, data_entry)
        else:
            insert_log_record(cursor, log_data)
        
        db_conn.commit()
    except mysql.connector.Error as e:
        db_conn.rollback()
        print(f"Error inserting log record: {e}")
        return "Error inserting log record", 500
    finally:
        cursor.close()
        db_conn.close()

    return "Log processed successfully", 200


def compare_notification_with_db(cursor, log_data, info_id, affairs_id):
    select_query = '''
        SELECT * FROM `Delete_Notification_logs_table` 
        WHERE `infoID` = %s AND `affairsID` = %s
    '''
    cursor.execute(select_query, (info_id, affairs_id))
    db_record = cursor.fetchone()

    if db_record:
        # 将数据库记录转换为字典格式
        db_record_dict = {
            'userID': db_record[0],
            'infoID': db_record[1],
            'affairsID': db_record[2],
            'deleteMethod': db_record[3],
            'deleteGranularity': db_record[4],
            'deleteNotifyTree': json.loads(db_record[-5]) if db_record[-5] else {}  # 转换为字典
            # ...其他字段...
        }

        # 对请求中的数据进行相同的转换（如果尚未转换）
        if 'deleteNotifyTree' in log_data and isinstance(log_data['deleteNotifyTree'], str):
            log_data['deleteNotifyTree'] = json.loads(log_data['deleteNotifyTree'])

        # 比较日志数据和数据库记录
        for key, value in log_data.items():
            if db_record_dict.get(key, None) != value:
                return False, f"Field mismatch for '{key}'. DB: {db_record_dict.get(key)}, Log: {value}"
        return True, "Notification logs match"
    else:
        return False, f"No record found with infoID {info_id} and affairsID {affairs_id}"

# def compare_notification_with_db(cursor, log_data, info_id, affairs_id):
#     select_query = '''
#         SELECT * FROM `Delete_Notification_logs_table` 
#         WHERE `infoID` = %s AND `affairsID` = %s
#     '''
#     cursor.execute(select_query, (info_id, affairs_id))
#     db_record = cursor.fetchone()

#     if db_record:
#             # 将数据库记录转换为字典格式
#             db_record_dict = {
#                 'userID': db_record[0],
#                 'infoID': db_record[1],
#                 'affairsID': db_record[2],
#                 'deleteMethod': db_record[3],
#                 'deleteGranularity': db_record[4],
#                 # ...其他字段...
#                 'deleteNotifyTree': json.loads(db_record[-5]) if db_record[-5] else {}  # Handling deleteNotifyTree at 5th from last
#             }

#             # 比较日志数据和数据库记录
#             for key, value in log_data.items():
#                 # 跳过数据库记录中为空的字段
#                 if db_record_dict.get(key) is None:
#                     continue

#                 if db_record_dict.get(key, None) != value:
#                     return False, f"Field mismatch for '{key}'. DB: {db_record_dict.get(key)}, Log: {value}"
#             return True, "Notification logs match"
#     else:
#         return False, f"No record found with infoID {info_id} and affairsID {affairs_id}"
    # if db_record:
    #     # 将数据库记录转换为字典格式
    #     db_record_dict = {
    #         'userID': db_record[0],
    #         'infoID': db_record[1],
    #         'affairsID': db_record[2],
    #         'deleteMethod': db_record[3],
    #         'deleteGranularity': db_record[4],
    #         `timeLimit` : db_record[5],
    #         `countLimit` : db_record[4],
    #         `deletePerformer` : db_record[4],
    #         `deletePerformTime`: db_record[4],
    #         `deleteDupinfoID` : db_record[4],
    #         `deleteInstruction`: db_record[4],
    #         `deleteControlSet` JSON DEFAULT NULL,
    #         `deleteAlg` INT DEFAULT NULL,
    #         `deleteAlgParam` VARCHAR(100) DEFAULT NULL,
    #         `deleteLevel` INT DEFAULT NULL,
    #         `deleteTriggers` VARCHAR(100) DEFAULT NULL,
    #         `abstract` TEXT DEFAULT NULL,
    #         `category` VARCHAR(100) DEFAULT NULL,
    #         `keyWords` VARCHAR(100) DEFAULT NULL,
    #         `title` TEXT DEFAULT NULL,
    #         `delConfirmSignatureDict` JSON DEFAULT NULL,
    #         `deleteConfirmation` VARCHAR(100) DEFAULT NULL,
    #         `deleteNotifyTree` JSON DEFAULT NULL,
    #         `classification_info` JSON DEFAULT NULL,
    #         `deleteIntention` TEXT DEFAULT NULL,
    #         `infoType` INT DEFAULT NULL,
    #         `deleteKeyinfoID` JSON DEFAULT NULL,
    #         'sourceDomainID': db_record[5] if len(db_record) > 5 else None,  # 检查字段是否存在
    #         'deleteNotifyTree': json.loads(db_record[-5]) if db_record[-5] else {}
    #     }

    #     # 比较日志数据和数据库记录
    #     for key, value in log_data.items():
    #         if db_record_dict.get(key, None) != value:  # 使用 get 方法获取值，如果不存在则返回 None
    #             return False, f"Field mismatch for '{key}'. DB: {db_record_dict.get(key)}, Log: {value}"
    #     return True, "Notification logs match"
    # else:
    #     return False, f"No record found with infoID {info_id} and affairsID {affairs_id}"

# def compare_notification_with_db(cursor, log_data, info_id, affairs_id):
#     select_query = '''
#         SELECT * FROM `Delete_Notification_logs_table` 
#         WHERE `infoID` = %s AND `affairsID` = %s
#     '''
#     cursor.execute(select_query, (info_id, affairs_id))
#     db_record = cursor.fetchone()
    
#     if db_record:
#             # 将数据库记录转换为字典格式
#             db_record_dict = {
#                 'userID': db_record[0],
#                 'infoID': db_record[1],
#                 'affairsID': db_record[2],
#                 'deleteMethod': db_record[3],
#                 'deleteGranularity': db_record[4],
#                 # ...其他字段
#                 'deleteNotifyTree': json.loads(db_record[-5]) if db_record[-5] else {}  # Handling deleteNotifyTree at 5th from last
#         }
         

#             # 比较日志数据和数据库记录
#             for key, value in log_data.items():
#                 if db_record_dict.get(key) != value:
#                     return False, f"Field mismatch for '{key}'. DB: {db_record_dict[key]}, Log: {value}"
#             return True, "Notification logs match"
#     else:
#         return False, f"No record found with infoID {info_id} and affairsID {affairs_id}"



def find_ips_in_config(config, local_ip):
    # 从配置文件中找到对应的IP地址
    for item in config['ip']:
        if item['3ip'] == local_ip:
            return item['1ip'], item['2ip']
    return None, None

def send_log_requests(infoID, affairsID, delete_notification_ip, deterministic_delete_ip):
    # 向相关系统发送日志请求
    send_log_request(f'http://{deterministic_delete_ip}:5000/getOperationLog', 'Delete_Operation', infoID, affairsID)
    send_log_request(f'http://{delete_notification_ip}:5000/getNotificationLog', 'Delete_Notification', infoID, affairsID)
    send_log_request(f'http://{delete_notification_ip}:5000/getConfirmationLog', 'Delete_Confirmation', infoID, affairsID)


def clean_data(data):
    # 处理 None 和 'null' 字符串
    for key, value in data.items():
        if value == 'null':
            data[key] = None
        # 进行其他必要的数据转换或默认值设置

    # 验证数据类型或值
    # 例如，如果某个字段期望是整数类型
    if 'timeLimit' in data and data['timeLimit'] is not None:
        try:
            data['timeLimit'] = int(data['timeLimit'])
        except ValueError:
            app.logger.error(f"Invalid data format for timeLimit: {data['timeLimit']}")
            data['timeLimit'] = None  # 或设置一个合理的默认值

    return data






def load_config2(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)


# 找到节点ID通过IP地址
def find_node_id_by_ip(ip_address, config):
    for node in config['nodes']:
        if node['ip'] == ip_address:
            print(f"Current node ID for IP {ip_address}: {node['system_id']}")
            return node['system_id']
    return None


def get_delete_notify_tree(infoID, affairsID, config):
    connection = mysql.connector.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_DATABASE)
    cursor = connection.cursor(dictionary=True)
    query = "SELECT `deleteNotifyTree` FROM `delete_Notification_logs_table` WHERE `infoID` = %s AND `affairsID` = %s"
    cursor.execute(query, (infoID, affairsID))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    if result:
        try:
            tree_str = result['deleteNotifyTree']
            print("Tree String:", tree_str)  # 调试输出
            tree = json.loads(tree_str)  # 可能只需要一次解析
            root_node_id = next(iter(tree))
            for node in config['nodes']:
                if node['system_id'] == root_node_id:
                    return tree, node
        except json.JSONDecodeError as e:
            print("Error: Unable to parse deleteNotifyTree as JSON. Error:", e)
            print("Invalid JSON String:", tree_str)  # 输出无法解析的字符串
        # try:
        #     tree= json.loads(result['deleteNotifyTree'])
        #     # 双重解析：先将字符串转为JSON，然后再解析得到的JSON
        #     # tree_str = json.loads(result['deleteNotifyTree'])
        #     # tree = json.loads(tree_str)
        #     root_node_id = next(iter(tree))
        #     for node in config['nodes']:
        #         if node['system_id'] == root_node_id:
        #             return tree, node
        # except json.JSONDecodeError:
        #     print("Error: Unable to parse deleteNotifyTree as JSON.")
    return None, None


def get_notification_data(cursor, infoID, affairsID):
    query = "SELECT `deleteNotifyTree` FROM `delete_Notification_logs_table` WHERE `infoID` = %s AND `affairsID` = %s"
    cursor.execute(query, (infoID, affairsID))
    data = cursor.fetchone()
    dict_data=json.loads(data[0])
    return dict_data if data else None


# def get_notification_data(cursor, infoID, affairsID):
#     query = "SELECT `deleteNotifyTree` FROM `delete_Notification_logs_table` WHERE `infoID` = %s AND `affairsID` = %s"
#     cursor.execute(query, (infoID, affairsID))
#     rows = cursor.fetchall()
#     if rows:
#         # 假设我们只关心第一行数据
#         first_row = rows[0]
#         # 检查返回的行是否为字典，并且包含 'deleteNotifyTree' 键
#         if isinstance(first_row, dict) and 'deleteNotifyTree' in first_row:
#             return first_row['deleteNotifyTree']
#     return []


def find_root_node(json_tree_str):
    try:
        # json_tree = json.loads(json_tree_str)
        return NotificationTreeUtils.get_root_node(json_tree_str)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None

def find_node_ip_by_id(config, node_id):
    for node in config['nodes']:
        if node['system_id'] == node_id:
            return node['ip']
    return None

# def send_info_to_root_node(root_node_ip, root_node_id ,data):
#     root_node_url = f'http://{root_node_ip}:5000/receive-node-info'
#     try:
#         print(123124)
#         response = requests.post(root_node_url, json=data)
#         if response.status_code == 200:
#             print("Info sent to root node successfully.")
#         else:
#             print(f"Failed to send info to root node. Status code: {response.status_code}")
#     except requests.RequestException as e:
#         print(f"Error sending request to root node: {e}")


# def report_error_to_root_node(root_node_ip, error_message):
#     root_node_url = f'http://{root_node_ip}:5000/receive-node-info'
#     payload = {'error_message': error_message}
#     try:
#         response = requests.post(root_node_url, json=payload)
#         if response.status_code == 200:
#             print("Error reported to root node successfully.")
#         else:
#             print(f"Failed to report error to root node. Status code: {response.status_code}")
#     except requests.RequestException as e:
#         print(f"Error sending request to root node: {e}")  

     
# def get_local_ip():
#     # 获取本机IP地址
#     s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     try:
#         # 这不需要是一个真实的地址，只是用于获取接口的IP地址
#         s.connect(('10.255.255.255', 1))
#         IP = s.getsockname()[0]
#     except Exception:
#         IP = '127.0.0.1'
#     finally:
#         s.close()
#     return IP

def get_evaluation_results(cursor, info_id, affairs_id):
    query = '''
        SELECT `deleteNotConComAnas`, `deleteConEvaRet`, `deleteMetComEvan`, 
               `deleteDupNonrecAsst`, `deleteOpeCorVern`, `deleteDupComVern`, `deleteEffectEvaRet`
        FROM `delete_EvalResult_table`
        WHERE `infoID` = %s AND `affairsID` = %s
    '''
    cursor.execute(query, (info_id, affairs_id))
    result = cursor.fetchone()
    if result:
        # Convert the tuple to a dictionary with field names
        field_names = ['deleteNotConComAnas', 'deleteConEvaRet', 'deleteMetComEvan', 
                       'deleteDupNonrecAsst', 'deleteOpeCorVern', 'deleteDupComVern', 'deleteEffectEvaRet']
        return dict(zip(field_names, result))
    return None
# def get_evaluation_results(cursor, info_id, affairs_id):
#     query = '''
#         SELECT `deleteNotConComAnas`, `deleteConEvaRet`, `deleteMetComEvan`, 
#                `deleteDupNonrecAsst`, `deleteOpeCorVern`, `deleteDupComVern`,`deleteEffectEvaRet`
#         FROM `delete_EvalResult_table`
#         WHERE `infoID` = %s AND `affairsID` = %s
#     '''
#     cursor.execute(query, (info_id, affairs_id))
#     return cursor.fetchone()


def fetch_notification_pairs(cursor):
    try:
        query = "SELECT DISTINCT `infoID`, `affairsID` FROM `delete_Notification_logs_table`"
        cursor.execute(query)
        return cursor.fetchall()
    except Error as e:
        print(f"Error fetching notification pairs: {e}")
        return []

@app.route('/evaluation-notification', methods=['POST'])
def receive_evaluation():

        data = request.json
        app.logger.info(f"Received evaluation notification: {data}")
        

        local_ip = "127.0.0.1"  # 获取本地 IP
        print("Local IP:", local_ip)
        # local_ip = get_local_ip()
    # local_ip = "127.0.0.1"  # 或者使用 get_local_ip()
    # print("Local IP:", local_ip)
        # 清洗和验证数据
        cleaned_data = clean_data(data)
        config = load_config('config3.json')
        local_ip = request.remote_addr
        infoID, affairsID = cleaned_data.get('infoID'), cleaned_data.get('affairsID')

        # 将收到的删除通知日志保存为文件
        infoID, affairsID = data.get('infoID'), data.get('affairsID')
        save_log(data, 'RootNotification', infoID, affairsID)
        
        delete_notification_ip, deterministic_delete_ip = find_ips_in_config(config, local_ip)
        if not delete_notification_ip or not deterministic_delete_ip:
            return jsonify({"status": "error", "message": "IP address not found in config"}), 404

        # 向相关系统发送日志请求
        send_log_request(f'http://{deterministic_delete_ip}:5000/getOperationLog', 'Delete_Operation', infoID, affairsID)
        send_log_request(f'http://{delete_notification_ip}:5000/getNotificationLog', 'Delete_Notification', infoID, affairsID)
        send_log_request(f'http://{delete_notification_ip}:5000/getConfirmationLog', 'Delete_Confirmation', infoID, affairsID)
        
        db_conn = connect_to_database()
        if db_conn is None:
            return jsonify({"status": "error", "message": "Database connection failed"}), 500

        cursor = db_conn.cursor()

        config2 = load_config2('config2.json')
        my_node_id = find_node_ip_by_id(config2, local_ip)
        #my_node_id = find_node_id_by_ip(local_ip, config2)
        # 处理日志数据
        status_message, status_code = process_log_data(cleaned_data, infoID, affairsID)
        if status_code != 200:
            return jsonify({"status": "error", "message": status_message}), status_code
     
        
        # 比较日志
        match, message = compare_notification_logs(cursor, data, infoID, affairsID)
        if not match:
            # 如果不匹配，报告错误给根节点
            local_ip = request.remote_addr
            config = load_config('config2.json')
            root_node_id = None  # 初始化 root_node_id
            notification_data = get_notification_data(cursor, infoID, affairsID)
            root_node_id = NotificationTreeUtils.get_root_node(notification_data)
            root_node_ip = find_node_ip_by_id(config, root_node_id)
            error_message = f"Notification logs mismatch on node: {root_node_id},ip: {root_node_ip}, infoID: {infoID}, affairsID: {affairsID}. {message}"
            return  jsonify({"status": "error", "message": error_message}), 400
            # report_error_to_root_node(root_node_ip,error_message)
            # if send_info_to_root_node(root_node_ip, root_node_id, {"error_message": error_message}):
            #     return jsonify({"status": "error", "message": error_message}), 400
            # else:
            #     return jsonify({"status": "error", "message": "Failed to report error to root node"}), 500 
            #return jsonify({"status": "error", "message": error_message}), 400
        else:
            # 如果匹配，继续执行完备性分析验证
            # perform_completeness_analysis(infoID, affairsID)
            #return 'ok'
            
            # print(root_node_id)
            # root_node_ip = find_node_ip_by_id(config, root_node_id)
            # print(root_node_id)
                



            db_connection = mysql.connector.connect(
        host='127.0.0.1', user='aa', password='123456', database='ab'
    )
            cursor = db_connection.cursor()
# 处理日志文件并插入到数据库
            local_files_directory = os.path.join("C:\\Users", "xu", "Documents", "GitHub", "1.6", "deleteEvaluationSystem")
            file_list = os.listdir(local_files_directory)
            filtered_file_list = [file for file in file_list if any(log_type in file for log_type in LOG_TYPES)]

            for file in filtered_file_list:
                file_path = os.path.join(local_files_directory, file)
                print(f"Processing file: {file_path}")  # 调试信息
                try:
                    process_json_file(cursor, file_path)
                    db_connection.commit()
                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")  # 异常处理
            # for file in filtered_file_list:
            #     process_json_file(cursor, os.path.join(local_files_directory, file))
            
            config = load_config('config2.json')
            # notification_data = get_notification_data(cursor, infoID, affairsID)
            # for data in notification_data:
            #     json_tree = json.loads(data['deleteNotifyTree'])
            #     root_node_id = NotificationTreeUtils.get_root_node(json_tree)
            root_node_id = None  # 初始化 root_node_id
            notification_data = get_notification_data(cursor, infoID, affairsID)
            root_node_id = NotificationTreeUtils.get_root_node(notification_data)
            root_node_ip = find_node_ip_by_id(config, root_node_id)
            # print("******************")
            # print(notification_data)
            # print(root_node_ip)

    #         for data in notification_data:
    #             json_tree = json.loads(data['deleteNotifyTree'])
    #             root_node_id = NotificationTreeUtils.get_root_node(json_tree)

    #             if root_node_id is not None:
    #                 print(root_node_id)
    #                 root_node_ip = find_node_ip_by_id(config, root_node_id)
    #                 print(root_node_id)
    #             else:
    # # 处理 root_node_id 未定义的情况
    #                 print("root_node_id is not defined.")



        #########################删除通知与确认完备性分析#########################
            db_connection = mysql.connector.connect(
                host='127.0.0.1', user='aa', password='123456', database='ab'
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
                #print(f"Processing pair: info_id={info_id}, affairs_id={affairs_id}")
                retention_client = RetentionStatusClient(info_id, affairs_id)
                response_file = retention_client.run()
                if response_file:
                    process_each_pair(info_id, affairs_id)
                # else:
                #     return 0#print(f"No response file for info_id={info_id}, affairs_id={affairs_id}")


        #########################删除操作正确性验证#########################
            id_pairs = fetch2_unique_id_pairs()
            for info_id, affairs_id in id_pairs:
                #print(f"Processing pair: info_id={info_id}, affairs_id={affairs_id}")
                retention_client = CombinedClient(info_id, affairs_id)
                result = retention_client.run()
                if result["success"]:
                    process2_each_pair(info_id, affairs_id)
                    # 处理其他逻辑
                # else:
                #     return 0#print(f"Error: {result['error_message']}")

            
        #########################删除评测结果汇总#########################
        #deleteEffectEvaRet整体删除效果评估结果     
            evaluator = DeleteEffectEvaluator('127.0.0.1', 'aa', '123456', 'ab')
            evaluator.run_evaluation()        
            # db_conn = connect_to_database()
            # if db_conn is not None:
            #     cursor = db_conn.cursor()
            #     create_eval_result_table_if_not_exists(cursor)
            #     update_delete_effect_eva_ret(cursor)

            #     db_conn.commit()
            
            eval_results = get_evaluation_results(cursor, info_id, affairs_id)
            if eval_results:
                eval_results_data = {
                    "infoID": info_id,
                    "affairsID": affairs_id,
                    "evaluation_results": eval_results
                }
                success_message = f"Notification logs match on node: {root_node_id},ip: {root_node_ip}, infoID: {infoID}, affairsID: {affairsID}. {eval_results_data}"
                return  jsonify({"status": "success", "message": success_message})
                # root_node_ip = 'root_node_ip'  # 根节点的 IP 地址
                # if send_info_to_root_node(root_node_ip, root_node_id,eval_results_data):
                #     return jsonify({"status": "success", "message": "Notification logs match and completeness analysis initiated"}), 200
                # else:
                #     return jsonify({"status": "error", "message": "Failed to send data to root node"}), 500
            else:
                return jsonify({"status": "error", "message": "No evaluation results found"}), 404


    #         # 处理删除确认日志
    #         confirmation_log_file = f"Delete_Confirmation_{infoID}_{affairsID}_log.json"
    #         process_and_insert_confirmation_log(confirmation_log_file)

    #         # 处理删除操作日志
    #         operation_log_file = f"Delete_Operation_{infoID}_{affairsID}_log.json"
    #         process_and_insert_operation_log(operation_log_file)
    #         db_connection.commit()
            # com_analysis = ComAnalysis(cursor)
            # com_analysis.perform_verification()
            # db_connection.commit()
            return jsonify({"status": "success", "message": "Notification logs match and completeness analysis initiated"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
    # except Exception as e:
    #     app.logger.error(f"Error processing request: {e}")
    #     return jsonify({"status": "error", "message": str(e)}), 500
    #     try:
    #         match, message = compare_notification_logs(cursor, cleaned_data, infoID, affairsID)
    #         if not match:
    #             error_message = f"Notification logs mismatch for infoID: {infoID}, affairsID: {affairsID} on node: {my_node_id},ip: {local_ip}. {message}"
    #             app.logger.warning(error_message)
    #             report_error_to_root_node(error_message)
    #             return jsonify({"status": "error", "message": error_message}), 400
    #         else:
    #             success_message = "Notification logs match"
    #             print(success_message)  # 打印匹配成功的信息
    #             return jsonify({"status": "success", "message": success_message})
            


        # notification_tree = get_notification_data(cursor, 'info_id_example', 'affairs_id_example')
        # root_node_id = find_root_node(notification_tree)
        # config = load_config('config2.json')
        # root_node_ip = find_node_ip_by_id(config, root_node_id)
        # if root_node_ip:
        #     send_info_to_root_node(root_node_ip, {'infoID': 'info_id_example', 'affairsID': 'affairs_id_example'})

    #     finally:
    #         cursor.close()
    #         db_conn.close()
    # except Exception as e:
    #     app.logger.error(f"Error processing request: {e}")
    #     return jsonify({"status": "error", "message": str(e)}), 500
        
    #     # 处理日志数据
    #     status_message, status_code = process_log_data(cleaned_data, infoID, affairsID)
    #     if status_code != 200:
    #         return jsonify({"status": "error", "message": status_message}), status_code

    #     # 连接数据库并比较日志
    #     db_conn = connect_to_database()
    #     if db_conn is None:
    #         return jsonify({"status": "error", "message": "Database connection failed"}), 500

    #     cursor = db_conn.cursor()
    #     try:
    #         match, message = compare_notification_logs(cursor, cleaned_data, infoID, affairsID)
    #         if not match:
    #             app.logger.warning(f"Mismatch found: {message}")
    #             return jsonify({"status": "error", "message": message}), 400
    #         return jsonify({"status": "success", "message": "Notification logs match"})
    #     finally:
    #         cursor.close()
    #         db_conn.close()

    # except Exception as e:
    #     app.logger.error(f"Error processing request: {e}")
    #     return jsonify({"status": "error", "message": str(e)}), 500


