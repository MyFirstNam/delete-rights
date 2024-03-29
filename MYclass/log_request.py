import json
import requests
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
from global_vars import evaluation_results_global

#########################删除日志请求#########################
#########################向删除通知与确认系统、确定性删除系统发送删除意图日志/删除请求日志/删除触发日志/删除通知日志/删除确认日志/删除操作日志日志请求#########################

# 发送日志请求
def send_log_request(server_url, log_type, infoID, time):
    headers = {'Content-Type': 'application/json'}
    payload = {
        "systemID": 1,
        "systemIP": "210.73.60.100",
        "mainCMD": 1,
        "subCMD": 32,
        "evidenceID": "00032dab40af0c56d2fa332a4924d150",
        "msgVersion": 4096,
        "submittime": "2023-11-08 00:15:28",
        "data": {
            "infoID": infoID if infoID else "",
            "time": time if time else "",
            "getLogType": f"get{log_type}Log"
        },
        "dataHash": "56e3be093f377b9d984eef02a982d852d1bce062fdb505bcf87df46141fd80aa",
        "datasign": "56e3be093f377b9d984eef02a982d852d1bce062fdb505bcf87df46141fd80aa"
    }

    response = requests.post(server_url, data=json.dumps(payload, ensure_ascii=False), headers=headers)
    
    global evaluation_results_global
    if response.status_code == 200:
        try:
            response_data = response.json()
            local_files_directory = os.path.join("C:\\Users", "xu", "Documents", "GitHub", "1.6", "log")
            os.makedirs(local_files_directory, exist_ok=True)  # 确保目录存在
            file_name = f"{log_type}_log.json"
            full_path = os.path.join(local_files_directory, file_name)
            with open(full_path, 'w', encoding='utf-8') as file:
                json.dump(response_data, file, indent=4)
            print(f"File saved: {full_path}")
        except json.JSONDecodeError:
            
            print(f"Error: Unable to parse JSON response from {server_url}")
    else:
        print(f"Error: Request to {server_url} failed with status code {response.status_code}")
    # if response.status_code == 200:
    #     try:
    #         response_data = response.json()
    #         file_name = f"{log_type}_log.json"  # 文件名现在只基于日志类型
    #         with open(file_name, 'w') as file:
    #             json.dump(response_data, file, indent=4)
    #         print(f"File saved: {file_name}")
    #     except json.JSONDecodeError:
    #         print(f"Error: Unable to parse JSON response from {server_url}")
    # else:
    #     print(f"Error: Request to {server_url} failed with status code {response.status_code}")


# 读取配置文件
def load_config(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# 根据IP找到相应的系统IP地址
def find_system_ips(config, my_ip):
    for item in config['ip']:
        if item['3ip'] == my_ip:
            return item['1ip'], item['2ip']
    return None, None
