# -*- coding: utf-8 -*-

from flask import Flask, request, jsonify
from StorageSystemClient import StorageSystemClient
import requests
import json
import os
import argparse
from datetime import datetime
from flask import current_app
from util import NotificationTreeUtils
import threading
import time
from service.classify_client import fetch_and_process_data
from service.store_client import query_data_and_key_locations
from service.command_gen import generate_delete_commands
from service.command_deliver import deliver_delete_commands
from service.log_save import save_operation_log

from service.command_deliver import TimeoutException
from service.command_deliver import DeleteFailException

from models.operation_log_model import OperationLogModel


# 确定性删除系统
# 1.2.1系统整体概述
# 确定性删除系统从删除指令通知与确认系统获得删除指令，并对指令进行解析，从而获取删除粒度、删除方法、全局性标识等字段，然后确定性删除系统将根据全局性标识从存储系统获得该个人信息包含的字段类型，并向分类分级系统查询这些字段类型对应的分类等级，确定性删除系统接下来将向存储系统查询该个人信息的存储类型、存储位置、密钥位置，并综合分类等级、存储类型、存储位置、密钥位置生成具体删除命令，并将删除命令发送到存储系统，删除系统执行删除之后，将向确定性删除系统汇报删除结果。
# 1.2.2 系统功能介绍
# 1.删除指令解析功能
# 从删除指令通知与确认系统获得删除指令之后，对删除指令按照通信协议进行解析，若各字段数据类型正确，则将正常获得删除粒度、删除方法等信息。
# 2.多副本确定功能已完成
# 确定性删除系统通过信息标识符向存储系统查询个人信息副本的存储位置，存储系统将个人信息副本位置返回
# 3.指令分解与下发功能已完成
# 确定性删除系统根据得到的个人信息存储位置、个人信息存储状态、密钥存储位置、个人信息字段类型分级等信息，生成删除命令，并将删除命令下发给存储系统
# 4.指令理解与方法选择功能已完成
# 确定性删除系统通过信息标识符向存储系统查询个人信息的字段类型，然后根据个人信息的字段类型向分类分级系统查询分级信息，并根据分级信息确定删除覆写次数
# 5.操作行为自存证功能已完成
# 确定性删除系统完成删除操作之后，将完成删除的过程中产生的各个字段保存为删除操作日志
# 6.证据提取功能已完成
# 确定性删除系统开启监听，当收到删除效果评测系统的日志提取请求之后，将提取相应的删除操作日志并发送给删除效果评测系统
# 7.密钥定位功能已完成
# 确定性删除系统通过信息标识符向存储系统查询个人信息的储存类型，如果是密文存储，则继续向存储系统查询密钥的存储位置，存储系统将密钥存储位置返回
# 8.操作执行功能已完成
# 确定性删除系统向存储系统发送删除命令，存储系统解析并执行删除命令，并将执行后的删除结果返回给确定性删除系统
# 9.	密钥删除功能已完成
# 确定性删除系统向存储系统发送密钥删除命令，存储系统解析并执行密钥删除命令，并将执行后的密钥删除结果返回给确定性删除系统
# 10.密钥分量确定与删除功能已完成
# 确定性删除系统通过信息标识符向存储系统查询个人信息的储存类型，如果是密文存储并且密钥是通过分散存储的形式进行存储，则向存储系统查询所有密钥分量的位置，存储系统将所有密钥分片的存储位置返回
# 11.操作反馈功能已完成
# 进行删除指令解析之后，确定性删除系统将得到发起删除的源域信息，如果当前域为源域，则在删除操作执行之后完之后等待其他域的删除结果，如果当前域不为源域，则在删除操作执行之后向源域报告删除结果
# 12.操作结果可视化功能未完成
# 源域的确定性删除系统在完成收集所有来自其他域的确定性删除系统的删除结果之后，通过可视化的方式展示最终的删除结果，即是否所有域都按要求完成了删除


# infoType 
# json 1
# txt 2
# video 3
# audio 4
# image 5
# other 6


#定义全局变量
node_statuses={}
status_updated = False
ifSendException = False
deletePerformer = "default Performer"
preset_duration_seconds=1

app = Flask(__name__)



# 函数：generate_delete_level
# 功能：根据最高信息级别生成删除级别
# 输入：
#    max_level: int - 最高信息级别
# 输出：
#    int - 计算出的删除级别
# def generate_delete_level(max_level):
#     if max_level == 5:
#         return 7
#     elif max_level in [3, 4]:
#         return 5
#     elif max_level in [1, 2]:
#         return 3
#     else:
#         return 1


# 函数：get_file_type
# 功能：根据文件列表中所有文件的统一扩展名返回对应的整数值
# 输入：
#    locations: list of str - 包含文件路径的字符串列表
# 输出：
#    int - 根据文件扩展名确定的文件类型对应的整数

# def get_file_type(locations):
#     # 如果提供的列表为空，返回 'other' 类型对应的整数 6
#     if not locations:
#         return 6
#
#     # 提取第一个文件的扩展名，并转换为小写以进行大小写不敏感的比较
#     file_extension = locations[0].split('.')[-1].lower()
#
#     # 定义文件类型与整数的对应关系
#     # 包括常见的视频、音频和图像文件类型
#     file_type_mapping = {
#         'json': 1,
#         'txt': 2,
#         'mp4': 3,
#         'avi': 3,
#         'mov': 3,
#         'wmv': 3,  # 视频文件类型
#         'mp3': 4,
#         'wav': 4,
#         'aac': 4,
#         'flac': 4,  # 音频文件类型
#         'jpg': 5,
#         'jpeg': 5,
#         'png': 5,
#         'gif': 5,
#         'bmp': 5,  # 图像文件类型
#     }
#
#     # 返回对应的整数，如果类型不在映射中，则返回 'other' 类型对应的整数
#     return file_type_mapping.get(file_extension, 6)




# 函数：generate_delete_command_str
# 功能：根据删除命令的JSON格式生成字符串形式的删除命令
# 输入：
#    command_json: dict - 包含删除命令信息的JSON对象
# 输出：
#    str - 格式化的删除命令字符串
# def generate_delete_command_str(command_json):
#     target = command_json.get("target", "")
#     deleteGranularity = command_json.get("deleteGranularity", None)
#     deleteAlg = command_json.get("deleteAlg", "")
#     deleteAlgParam = command_json.get("deleteAlgParam", "")
#     deleteLevel = command_json.get("deleteLevel", "")
#
#     if deleteGranularity:
#         command_str = f"delete {deleteGranularity} of {target} using deleteAlg={deleteAlg} with deleteAlgParam={deleteAlgParam} at deleteLevel= {deleteLevel}"
#     else:
#         command_str = f"delete {target} using deleteAlg={deleteAlg} with deleteAlgParam={deleteAlgParam} at deleteLevel= {deleteLevel}"
#
#     return command_str

# 函数：parse_arguments
# 功能：解析命令行参数
# 输入：
#    无
# 输出：
#    argparse.Namespace - 解析后的命令行参数
def parse_arguments():
    parser = argparse.ArgumentParser(description='Flask Node Startup Configuration')
    parser.add_argument('system_id', help='Name of the node to start')
    return parser.parse_args()

# 函数：load_del_config
# 功能：加载指定系统标识的配置信息
# 输入：
#    system_id: str - 系统标识符
# 输出：
#    dict 或 None - 成功时返回配置信息字典，失败时返回 None
# def load_del_config(system_id):
#     try:
#         with open('config.json', 'r') as file:
#             config = json.load(file)
#             for node in config['nodes']:
#                 if node['system_id'] == system_id:
#                     return node
#     except FileNotFoundError:
#         print("配置文件未找到。请确保 config.json 文件在正确的位置。")
#     except json.JSONDecodeError:
#         print("配置文件格式错误。请确保它是有效的 JSON 格式。")
#     except Exception as e:
#         print(f"读取配置文件时发生错误：{e}")
#
#     return None


# 函数：load_store_config
# 功能：加载指定系统标识的配置信息
# 输入：
#    system_id: str - 系统标识符
# 输出：
#    dict 或 None - 成功时返回配置信息字典，失败时返回 None
# def load_store_config(system_id):
#     try:
#         with open('config.json', 'r') as file:
#             config = json.load(file)
#             for node in config['storeSystem']:
#                 if node['system_id'] == system_id:
#                     return node
#     except FileNotFoundError:
#         print("配置文件未找到。请确保 config.json 文件在正确的位置。")
#     except json.JSONDecodeError:
#         print("配置文件格式错误。请确保它是有效的 JSON 格式。")
#     except Exception as e:
#         print(f"读取配置文件时发生错误：{e}")
#
#     return None



# 函数：load_classify_config
# 功能：加载系统的配置信息
# 输入：
#    无
# 输出：
#    tuple - 包含分类系统和存储系统配置的元组，失败时返回 (None, None)
def load_classify_config():
    try:
        with open('config.json', 'r') as file:
            config = json.load(file)

            # 提取 classifySystem 和 storeSystem 的配置
            classify_system_config = config.get("classifySystem")
            # store_system_config = config.get("storeSystem")

            return classify_system_config

    except FileNotFoundError:
        print("配置文件未找到。请确保 config.json 文件在正确的位置。")
    except json.JSONDecodeError:
        print("配置文件格式错误。请确保它是有效的 JSON 格式。")
    except Exception as e:
        print(f"读取配置文件时发生错误：{e}")

    return None, None

# 函数：send_deletion_message
# 功能：向根节点发送删除消息
# 输入：
#    rootNode: str - 根节点的系统标识符
#    system_id: str - 当前系统的标识符
#    final_status: str - 最终状态信息
# 输出：
#    无直接输出，但会向根节点发送 POST 请求
def send_deletion_message(rootNode,system_id, final_status):
    # 从配置文件中加载根节点信息
    root_node_config = load_del_config(rootNode)
    if root_node_config is None:
        print("无法加载根节点配置。")
        return

    root_node_ip = root_node_config['ip']
    root_node_port=root_node_config['port']

    # 构造数据包
    data = {'node_id':system_id,'status': final_status}

    # 发送 POST 请求到根节点的 /gatherResult 路由
    url = f'http://{root_node_ip}:{root_node_port}/gatherResult'
    try:
        response = requests.post(url, json=data)
        print(f"Message sent to root node. Response: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error sending message to root node: {e}")

# 函数：wait_for_results
# 功能：等待并显示删除结果
# 输入：
#    timeout: int - 等待结果的超时时间（秒）
# 输出：
#    无直接输出，但会打印每个节点的状态和超时后的结果
def wait_for_results(timeout):
    print(f"开始等待来自{list(node_statuses.keys())}的删除结果")
    global status_updated
    start_time = time.time()
    while time.time() - start_time < timeout:
        if status_updated:
            # 显示每个节点的当前状态
            for node, status in node_statuses.items():
                print(f"节点 {node} 状态: {status}")
            status_updated = False  # 重置标志

        if all(status == 'success' for status in node_statuses.values()):
            print("所有节点都成功报告了删除结果。")
            return
        time.sleep(1)  # 等待一秒再次检查

    # 超时后检查未成功报告的节点
    for node, status in node_statuses.items():
        if status != 'success':
            print(f"节点 {node} 未成功报告删除结果。")


# 路由：/gatherResult
# 功能：接收节点的删除结果并更新状态
# 输入：
#    无（使用 Flask 的 request.json 获取输入数据）
# 输出：
#    JSON - 返回结果接收确认或错误信息
@app.route('/gatherResult', methods=['POST'])
def gather_result():
    global status_updated
    data = request.json
    node_id = data.get('node_id')
    status = data.get('status')

    if node_id and status:
        node_statuses[node_id] = status
        status_updated = True  # 标记状态已更新
        return jsonify({"message": "Result received"}), 200
    else:
        return jsonify({"error": "Invalid data received"}), 400
    

#模拟邓鑫系统
@app.route('/getIntentLog', methods=['POST'])
def get_intention_log():
    # 文件路径
    file_path = './log/Delete_Intent_log.json'





    # 从文件中读取 JSON 数据
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return jsonify(data)

@app.route('/getRequestLog', methods=['POST'])
def get_request_log():
    # 文件路径
    file_path = './log/Delete_Request_log.json'

    # 从文件中读取 JSON 数据
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return jsonify(data)


@app.route('/getTriggerLog', methods=['POST'])
def get_trigger_log():
    # 文件路径
    file_path = './log/Delete_Trigger_log.json'

    # 从文件中读取 JSON 数据
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return jsonify(data)
@app.route('/getNotificationLog', methods=['POST'])
def get_notification_log():
    # 文件路径
    file_path = './log/Delete_Notification_log.json'

    # 从文件中读取 JSON 数据
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return jsonify(data)

@app.route('/getConfirmationLog', methods=['POST'])
def get_confirmation_log():
    # 文件路径
    file_path = './log/Delete_Confirmation_log.json'

    # 从文件中读取 JSON 数据
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    return jsonify(data)

# 路由：/getOperationLog
# 功能：根据请求数据获取操作日志
# 输入：
#    无（使用 Flask 的 request.get_json() 获取输入数据）
# 输出：
#    JSON - 返回操作日志或错误信息
@app.route('/getOperationLog', methods=['POST'])
def get_operation_log():
    try:
        # 从 POST 请求中解析 JSON 数据
        data = request.get_json()

        print(data)

        # 解析基本字段
        # 假设 data 是一个字典，包含各种可能的键值对

        # 检查是否存在 'systemID'，如果存在，则获取 system_id 的值
        if 'systemID' in data:
            system_id = data.get('systemID')  # 系统ID

        # 检查是否存在 'systemIP'，如果存在，则获取 system_ip 的值
        if 'systemIP' in data:
            system_ip = data.get('systemIP')  # 系统IP地址

        # 检查是否存在 'mainCMD'，如果存在，则获取 main_cmd 的值
        if 'mainCMD' in data:
            main_cmd = data.get('mainCMD')  # 主命令

        # 检查是否存在 'subCMD'，如果存在，则获取 sub_cmd 的值
        if 'subCMD' in data:
            sub_cmd = data.get('subCMD')  # 子命令

        # 检查是否存在 'evidenceID'，如果存在，则获取 evidence_id 的值
        if 'evidenceID' in data:
            evidence_id = data.get('evidenceID')  # 证据ID

        # 检查是否存在 'msgVersion'，如果存在，则获取 msg_version 的值
        if 'msgVersion' in data:
            msg_version = data.get('msgVersion')  # 消息版本

        # 检查是否存在 'submittime'，如果存在，则获取 submittime 的值
        if 'submittime' in data:
            submittime = data.get('submittime')  # 提交时间

        # 检查是否存在 'dataHash'，如果存在，则获取 data_hash 的值
        if 'dataHash' in data:
            data_hash = data.get('dataHash')  # 数据哈希

        # 检查是否存在 'datasign'，如果存在，则获取 datasign 的值
        if 'datasign' in data:
            datasign = data.get('datasign')  # 数据签名


        #对infoID的解析
        # 检查 'data' 键是否存在于 data 字典中且其值是否为一个字典
        if 'data' in data and isinstance(data['data'], dict):
            # 提取 'affairsID' 字段
            # 如果 'data' 字典中存在 'affairsID'，则获取其值，否则设为默认空字符串
            affairsID = data['data'].get('affairsID', '')

            # 提取 'infoID' 字段
            # 如果 'data' 字典中存在 'infoID'，则获取其值，否则设为默认空字符串
            infoID = data['data'].get('infoID', '')

            # 提取 'time' 字段
            # 如果 'data' 字典中存在 'time'，则获取其值，否则设为默认空字符串
            time_str = data['data'].get('time', '')
        else:
            # 如果 'data' 键不存在或其值不是字典，则将所有字段设为默认空字符串
            affairsID = ''
            infoID = ''
            time_str = ''


        # 特别处理 'data' 字典内的 'time' 字段
        start_time, end_time = None, None
        if 'to' in time_str:
            start_time_str, end_time_str = time_str.split(' to ')
            start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
            end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S')

        print(start_time, end_time)

        #  这行是操作数据库
        db_model = OperationLogModel("127.0.0.1", "root", "123456", "assured_deletion")

        if infoID and affairsID:
            result_json = db_model.get_records_by_infoID_affairsID(infoID, affairsID)

        elif  not infoID:
            result_json = db_model.get_records_by_time_period(start_time, end_time)

        elif  not time_str:
            result_json = db_model.get_records_by_infoID(infoID)
        
        else:
            return jsonify({"error": "wrong request format"}), 500

        op_log=db_model.format_log(result_json)

        return jsonify(op_log)


        # filename=infoID+"_"+affairsID

        # # 构建文件路径
        # file_path = os.path.join('log', f"{filename}.json")
        
        # # 检查文件是否存在
        # if os.path.exists(file_path):
        #     with open(file_path, 'r') as file:
        #         log_data = json.load(file)
        #         return jsonify(log_data)
        # else:
        #     return jsonify({"error": "Log not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/getInstruction', methods=['POST'])
def get_instruction():
    try:
        # 获取JSON数据
        outside_data = request.json
        data = outside_data.get("data")

#########################删除通知解析#########################
        print("\n------------------------------")
        print("Delete Notification Parsed")
        print("------------------------------")

        #解析外部的字段
        notifySystemID = outside_data.get("systemID")
        notifySystemIP = outside_data.get("systemIP")
        notifyTime = outside_data.get("time")

        # 解析内部data字段的值
        systemID=current_app.config.get('SYSTEM_ID')
        affairsID = data.get("affairsID")
        userID = data.get("userID")
        infoID = data.get("infoID")
        deleteMethod = data.get("deleteMethod")
        deleteGranularity = data.get("deleteGranularity")
        deleteNotifyTree= json.loads(data.get("deleteNotifyTree"))
        parentNode = NotificationTreeUtils.find_parent(deleteNotifyTree, systemID)
        rootNode = NotificationTreeUtils.get_root_node(deleteNotifyTree)
        otherNode=NotificationTreeUtils.find_all_nodes_except(deleteNotifyTree, systemID)

        isRoot=False
        if systemID==rootNode:
            isRoot=True
        
        delete_instruction_str=f"在{notifyTime}时间下发以{deleteMethod}方式删除{infoID}信息的{deleteGranularity}的指令"
        
        print(f"Submit Time: {notifyTime}")
        print(f"Affairs ID: {affairsID}")
        print(f"User ID: {userID}")
        print(f"Info ID: {infoID}")
        print(f"Delete Method: {deleteMethod}")
        print(f"Delete Granularity: {deleteGranularity}")
        print(f"Delete NotifyTree: {deleteNotifyTree}")
        print(f"Parent Node: {parentNode}")
        print(f"Root Node: {rootNode}")
        print(f"Other Node: {otherNode}")
        print(f"Myself: {systemID}")

#########################分类分级信息获取#########################
        print("\n------------------------------")
        print("Classification Information")
        print("------------------------------")

        sorted_data, max_level = fetch_and_process_data(infoID,app.config['store_system_ip'],app.config['store_system_port'],app.config['classify_system_ip'],app.config['classify_system_port'])

        print(f"Max Sensitive Level: {max_level}")
        print(f"Classified Information: {sorted_data}")



#########################副本及密钥信息#########################
        print("\n------------------------------")
        print("Duplication and Key Information")
        print("------------------------------")

        locations,key_locations,key_status=query_data_and_key_locations(infoID,app.config['store_system_ip'],app.config['store_system_port'])
        print(f"Locations for infoID {infoID}: {locations}")
        print(f"Key locations for infoID {infoID}: {key_locations}")
        print(f"Key status for infoID {infoID}: {key_status}")

        infoType=get_file_type(locations)


#########################删除命令生成#########################
        print("\n------------------------------")
        print("Delete Commands")
        print("------------------------------")

        duplicationDelCommand,keyDelCommand=generate_delete_commands(app.config['store_system_ip'],app.config['store_system_port'], max_level, infoID, locations, key_locations, deleteGranularity, deleteMethod,infoType,affairsID)

        duplicationDelCommand_str=generate_delete_command_str(duplicationDelCommand)
        print(f"Duplication Delete Command: {duplicationDelCommand_str}")


        if keyDelCommand:
            #如果keyDelCommand存在的话
            keyDelCommand_str=generate_delete_command_str(keyDelCommand)
            print(f"Key Delete Command: {keyDelCommand_str}")
        else:
            #如果keyDelCommand不存在
            keyDelCommand_str="no need for key deletion command"
            print("The information is plaintext, there is no key deletion command")



#########################删除命令发送#########################
        print("\n------------------------------")
        print("Delete Command Deliveried")
        print("------------------------------")
        
        # 初始化最终状态为成功
        final_status = "success"

        final_status,deletePerformTime=deliver_delete_commands(app.config['store_system_ip'],app.config['store_system_port'], duplicationDelCommand, keyDelCommand, infoID, affairsID, delete_instruction_str, deletePerformer, preset_duration_seconds,key_status)
        



#########################存证信息#########################
        print("\n------------------------------")
        print("Evidence Record")
        print("------------------------------")
        # 创建完整版存证的JSON对象

        # 定义全局变量-数据包头
        systemIP = "210.73.60.100"
        mainCMD = 0x0001
        subCMD = 0x0020
        evidenceID = "00032dab40af0c56d2fa332a4924d150"
        msgVersion = 0x1000
        submittime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 定义"data"字段中的子字段
        title = f"系统{systemID}删除{infoID}文件存证记录"
        abstract = f"系统{systemID}采用算法集合{deleteMethod}删除{infoID}文件存证记录"
        keyWords = "删除"
        category = "12-345624"
        others = "none"
        # infoID = "BA4A7F24-ACA7-4844-98A5-464786DF5C09"
        infoType = 1
        # deletePerformTime = "2022-12-13 09:24:34"
        deleteDupinfoID = locations
        deleteControlSet=duplicationDelCommand_str+" and "+keyDelCommand_str
        deleteAlg_num=1


        # 定义其他字段
        deleteLevel=generate_delete_level(max_level)
        deleteAlgParam=infoID
        dataHash = "56e3be093f377b9d984eef02a982d852d1bce062fdb505bcf87df46141fd80aa"
        datasign = "56e3be093f377b9d984eef02a982d852d1bce062fdb505bcf87df46141fd80aa"

        fullEvidence = {
            "systemID": systemID,
            "systemIP": systemIP,
            "mainCMD": mainCMD,
            "subCMD": subCMD,
            "evidenceID": evidenceID,
            "msgVersion": msgVersion,
            "submittime": submittime,
            "data": {
                "globalID":infoID,
                "status":"已删除",
                "title": title,
                "abstract": abstract,
                "keyWords": keyWords,
                "category": category,
                "infoType": infoType,
                "deletePerformer": deletePerformer,
                "deletePerformTime": deletePerformTime,
                "deleteDupinfoID": deleteDupinfoID,
                "deleteInstruction": {
                        "userID": userID,
                        "infoID":infoID,
                        "deleteMethod": deleteMethod,
                        "deleteGranularity":deleteGranularity
                },
                "deleteControlSet": deleteControlSet,
                "deleteAlg": deleteAlg_num,
                "deleteAlgParam": deleteAlgParam,
                "deleteLevel": deleteLevel,
                "pathtree": {
                    "parent":{
                        "systemID":1,
                        "globalID":"时间戳+随机数+产生信息系统名字"
                    },
                    "self":{
                        "systemID":1,
                        "globalID":"时间戳+随机数+产生信息系统名字",
                        "evidenceID":"00032dab40af0c56d2fa332a4924d150"
                    },
                    "child":{
                        "systemID":0,
                        "globalID":""
                    }
                }},

            "dataHash": dataHash,
            "datasign": datasign
        }

        # 使用 json.dumps 打印格式化的 JSON
        print(json.dumps(fullEvidence, indent=4, ensure_ascii=False))


#########################删除操作日志处理#########################
        print("\n------------------------------")
        print("Operation Log")
        print("------------------------------")

        fullEvidence['data']['classification_info']=sorted_data
        fullEvidence['data']['deleteKeyinfoID']=key_locations
        fullEvidence['data']['infoID']=fullEvidence['data']['globalID']
        fullEvidence['data']['affairsID']=affairsID
        fullEvidence['data']['userID']=userID
        fullEvidence['data']['deleteMethod']=deleteMethod
        fullEvidence['data']['deleteGranularity']=deleteGranularity
        fullEvidence['isRoot']=isRoot
        del fullEvidence['data']['globalID']



        print(fullEvidence)

        # 确保log文件夹存在，不存在则创建
        log_dir = "log"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # 检查 infoID 是否存在
        if infoID:
            # 构建目标文件路径
            target_file_path = os.path.join(log_dir, f"{infoID}_{affairsID}.json")

            # 打开文件并写入操作日志
            with open(target_file_path, 'w', encoding='utf-8') as target_file:
                # 使用 json.dump 将操作日志转换为 JSON 格式并保存
                json.dump(fullEvidence, target_file, ensure_ascii=False, indent=4)

            # 输出保存成功的消息
            print(f"File saved as {target_file_path}")
        else:
            # infoID 不存在时的错误提示
            print("infoID not found in operation_log dictionary")


        save_operation_log(fullEvidence, affairsID, userID, sorted_data, deleteMethod, deleteGranularity, key_locations, infoID,isRoot)

#########################删除结果汇总#########################
        print("\n------------------------------")
        print("Delete Result Collected")
        print("------------------------------")
        if isRoot==True:
            if otherNode==[]:
                print("Root node is the only node, deletion completed")
            else:
                global node_statuses  # 指定接下来使用的是全局变量
                node_statuses = {node: 'pending' for node in otherNode}
                # 启动等待结果的线程
                timeout = 60  # 设置超时时间
                wait_thread = threading.Thread(target=wait_for_results, args=(timeout,))
                wait_thread.start()
        else:
            print("sending results to the root code")
            send_deletion_message(rootNode,systemID,final_status)
            #向源域节点发送消息

        
#########################成功返回#########################
        return jsonify({"message": "Data received and parsed successfully!"}), 200

#########################异常处理#########################
        print("\n------------------------------")
        print("Exception Occurs")
        print("------------------------------")
    except DeleteFailException as e:
        print("\n------------------------------")
        print("Delete Failure Exception Captured")
        print("------------------------------")
        error_data = e.error_data
        infoID = error_data["data"]["content"]["infoID"]
        affairsID = error_data["data"]["content"]["affairsID"]
        with open(f'./err2/{infoID}-{affairsID}.json', 'w') as f:
            json.dump(error_data, f,indent=4)

        print(f"error log is saved as ./err2/{infoID}-{affairsID}.json")

        if ifSendException:
            # 发送数据包到远程主机的代码 ...
            pass

        return jsonify({"error": str(e)}), 400

    except TimeoutException as e:
        print("\n------------------------------")
        print("Time Out Exception Captured")
        print("------------------------------")
        error_data = e.error_data
        infoID = error_data["data"]["content"]["infoID"]
        affairsID = error_data["data"]["content"]["affairsID"]
        with open(f'./err1/{infoID}-{affairsID}.json', 'w') as f:
            json.dump(error_data, f,indent=4)

        print(f"error log is saved as ./err1/{infoID}-{affairsID}.json")

        if ifSendException:
            # 发送数据包到远程主机的代码 ...
            pass

        return jsonify({"error": str(e)}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# if __name__ == "__main__":
#     app.run()
    # app.run(host='10.12.170.110')

if __name__ == "__main__":
    args = parse_arguments()
    node_config = load_del_config(args.system_id)
    classify_system_config = load_classify_config()
    store_system_config = load_store_config(args.system_id)

    if node_config:
        app.config['SYSTEM_ID'] = args.system_id  # Store system_id in app.config
        app.config['HOST'] = node_config['ip']
        app.config['PORT'] = node_config['port']

        # Store classifySystem configuration in app.config
        if classify_system_config:
            app.config['classify_system_ip'] = classify_system_config['ip']
            app.config['classify_system_port'] = classify_system_config['port']
        else:
            print("No configuration found for classifySystem")

        # Store storeSystem configuration in app.config
        if store_system_config:
            app.config['store_system_ip'] = store_system_config['ip']
            app.config['store_system_port'] = store_system_config['port']

        else:
            print("No configuration found for storeSystem")

        app.run(host=node_config['ip'], port=node_config['port'])
    else:
        print(f"No configuration found for node {args.system_id}")