import requests

from DelTrigger import DelTrigger
import csv
import json
from Json2Tree import json2tree
from ConnectOne import ConnectOne
from Path2Json import gen_tree_json
import pprint
import datetime
from DataExist import is_database_exists, database_create
from InfoMemory import InfoMemory
import configparser

def print_with_timestamp(message):
    current_time = datetime.datetime.now()
    timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


class DellntentionAly:
    # 功能：发出删除意图（一个字典）
    def __init__(self, delintention, Bus_id):
        self.delintention = delintention
        self.Bus_id = Bus_id

    def Intention(self):
        # 接收到删除意图
        # 三种情况，普通请求，带有时间请求，带有次数次数请求
        trigger = DelTrigger()
        if "time_limit" in self.delintention and "count_limit" not in self.delintention:
            deleteReq = trigger.timeTrigger(self.delintention)  # 函数返回值删除请求，为一个dict
            Timememory = self.delintention["time_limit"]
            Countmemory = 0
            triggerType = "计时触发"
        elif "time_limit" not in self.delintention and "count_limit" in self.delintention:
            deleteReq = trigger.countTrigger(self.delintention)
            Timememory = ""
            Countmemory = self.delintention["count_limit"]
            triggerType = "计次触发"
        else:
            deleteReq = trigger.deleteTrigger(self.delintention)
            Timememory = ""
            Countmemory = 0
            triggerType = "按需触发"
        # 获取到删除请求（已经从删除意图解析成为了删除请求）
        print_with_timestamp(f'删除请求已成功生成！')

        # 向中心监管机构请求删除流转路径
        with open('ID.csv', 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['ID'] == "b1099":  # 默认中心监管机构的ID是b1099
                    port = row['port']
                    ip = row['IP']

        connectone = ConnectOne(ip, port)
        dataTransferPath = connectone.reqPah(deleteReq["affairs_id"], deleteReq["info_id"])
        dataTransferPath = json.loads(dataTransferPath)
        print_with_timestamp("——————————————————————————————通知范围确定——————————————————————————————")
        deleteNotifyTree = gen_tree_json(dataTransferPath, self.Bus_id)
        # deleteNotifyTree 样例
        # {"b1000": {"children": [{"b1001": {"children": ["b1002"]}}, {"b1003": {"children": ["b1004"]}}]}}

        # todo 注意格式
        # todo run app.py
        url = "http://127.0.0.1:20098/update_graph"
        response = requests.post(url, json=deleteNotifyTree)
        if response.status_code == 200:
            print_with_timestamp("传播树同步成功！")
        else:
            print_with_timestamp("传播树同步失败！")

        tree = json2tree(deleteNotifyTree)
        print_with_timestamp(f'接收到的数据流转路径经过格式转换后如下:')
        print(tree)

        # 删除通知生成与分发
        # (1) 首先生成删除通知
        # (2) 当前节点，通过deleteNotifyTree,得到后继节点，即后面应该发给那些节点（如果当前节点直接就是叶子节点，则不需要转发，直接返回一个true）

        # nextNode = [i._identifier for i in tree.children(self.Bus_id)]  # 负责根据当前节点，寻找下一个节点（子节点的所有唯一标识符id），返回一个list

        # (1-1)生成删除通知，将deleteReq与deleteNotifyTree结合一下
        delNotice = {
            "affairs_id": deleteReq["affairs_id"],
            "user_id": deleteReq["user_id"],
            "info_id": deleteReq["info_id"],
            "from_bus_id": self.Bus_id,
            "to_bus_id": "",  # 实现过程中，此参数应该是一个字符串，表示后续发送给某一个节点，在生成删除通知时需要根据情况更新
            "deleteMethod": deleteReq["deleteMethod"],
            "deleteGranularity": deleteReq["deleteGranularity"],
            "deleteNotifyTree": deleteNotifyTree  # 一个JSON
        }
        # 示例用法
        print_with_timestamp("——————————————————————————————删除通知生成——————————————————————————————")
        print_with_timestamp(f'本企业{self.Bus_id}已根据删除流转树等信息成功生成删除通知，删除通知内容如下：')
        pprint.pprint(delNotice)


        # 创建ConfigParser对象
        config = configparser.ConfigParser()
        # 读取配置文件
        config.read('config.ini')
        # 从配置文件中获取值
        host = config.get('Database', 'host')
        user = config.get('Database', 'user')
        password = config.get('Database', 'password')
        port = config.getint('Database', 'port')
        database = config.get('Database', 'database_prefix')
        database = database + self.Bus_id

        if is_database_exists(host, user, password, database):
            print_with_timestamp("企业本地存证数据库已经存在，对删除通知信息正在本地存证···")
            processor = InfoMemory(host=host, user=user, port=port, password=password, database=database)
            # processor.insert_record(delNotice["user_id"], delNotice["info_id"],delNotice["deleteMethod"],delNotice["deleteGranularity"],delNotice["deleteNotifyTree"],triggerType,self.Bus_id,Timememory,Countmemory)
            processor.insert_record(delNotice["affairs_id"], delNotice["user_id"], delNotice["info_id"], delNotice["deleteMethod"], delNotice["deleteGranularity"], delNotice["deleteNotifyTree"], triggerType, self.Bus_id, Timememory, Countmemory)
        else:
            print_with_timestamp(f"企业数据库不存在，正在新建数据库···数据库名为{database}")
            database_create(host, user, password, port, database)
            print_with_timestamp(f"企业数据库已经新建完毕！")
            processor = InfoMemory(host=host, user=user, port=port, password=password, database=database)
            # processor.insert_record(delNotice["user_id"], delNotice["info_id"],delNotice["deleteMethod"],delNotice["deleteGranularity"],delNotice["deleteNotifyTree"],triggerType,self.Bus_id,Timememory,Countmemory)
            processor.insert_record(delNotice["affairs_id"], delNotice["user_id"], delNotice["info_id"],delNotice["deleteMethod"], delNotice["deleteGranularity"],delNotice["deleteNotifyTree"], triggerType, self.Bus_id, Timememory, Countmemory)

        # 存储目前已经获取的信息
        # processor = InfoMemory(host="localhost", user="root", port=3306, password="123456", database="project26")
        # processor = InfoMemory(host="10.170.42.45", port=3306, user="myuser", password="mypassword", database="project26")
        # processor.insert_record(delNotice["user_id"], delNotice["info_id"],delNotice["deleteMethod"],delNotice["deleteGranularity"],delNotice["deleteNotifyTree"],triggerType,Bus_id,Timememory,Countmemory)

        print_with_timestamp(f'当前可以获取的信息已经存储在企业本地数据库！')
        return delNotice
