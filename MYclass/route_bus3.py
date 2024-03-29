import cryptography
from flask import Flask, request, jsonify, Blueprint
from MYclass.ConnectSysDel import ConnectSysDel
from MYclass.DelTrigger import DelTrigger
import ConnectOne
import asynfunction
import asyncio
import requests
import json
import hashlib
import csv
from MYclass import DelNotifyOther, SignAndKey
from MYclass.Json2Tree import json2tree
from MYclass.PathSelect import PathSelect, TreeParentFinder
from Confirm_bus3 import confirm3

route3 = Blueprint("userroute1", __name__)

# 用于记录已经接收到的删除确认个数
# recvAckDict = {
#    # "affairs_id": [2, {"bx1000": "0xasdas"}, {"bx1001": "0xasdfas"}]
# }

# todo 每次启动路由，标识当前路由（企业）ID，通过外部标识输入参数
Bus_id = "b1003"

userroute3 = Flask(__name__)
@userroute3.route("/test/postx/endpointx", methods=['POST'])
def notifyAcc():
    delNotice = request.json  # data已经是一个字典，接收到的是删除通知
    delNotice = json.loads(delNotice)
    print("本节点"+Bus_id+"收到信息")
    # 第一个异步函数负责下发删除通知
    # 调用 asynfunction.py 中的异步函数,异步函数负责实现除去返回删除通知应答的所有功能
    #asynfunction.processNotify(delNotice, Bus_id)
    #这里不需要执行异步函数了，后续的列表中直接执行

    # 第二个异步函数返回删除通知应答     #todo 对于接接收删除通知应答还需要考虑,考虑删除通知应答反馈给谁
    async def delresponse(data):
        # 生成删除通知应答
        tree = json2tree(delNotice["deleteNotifyTree"])
        # node = tree.parent(Bus_id)._identifier
        node = tree.parent(Bus_id)
        DelNoticeResponse = {
            "affairs_id": data["affairs_id"],
            "from_bus_id": Bus_id,
            "to_bus_id": node,   # todo 考虑是返回给父节点，还是源节点，如果返回给源节点，还需要查询源节点的信息
            "user_id": data["user_id"],
            "info_id": data["info_id"],
            "isReceive": True,
        }
        print("删除通知应答响应成功！")
        print("本节点"+Bus_id+"父节点是：", node)
        #todo 删除通知应答问题怎么办？？？？？
        # 发送删除通知应答，查询发送端的IP和port
        # ip = "202.202.202.20"
        # port = 10001
        # # 把字典格式转为JSON
        # DelResponse = json.dumps(DelNoticeResponse)
        # url = f"http://{ip}:{port}/your/post/endpoint"  # 替换为自己的实际目标URL
        # response = requests.post(url, json=DelResponse)
        # # 检查响应
        # if response.status_code == 200:
        #     print("POST请求成功")
        #     print("响应内容:", response.text)
        # else:
        #     print("POST请求失败")
        #     print("响应状态码:", response.status_code)

    task_list = [asynfunction.processNotify(delNotice, Bus_id), delresponse(delNotice)]
    asyncio.run(asyncio.wait(task_list))
    return "接收成功！"

if __name__ == "__main__":
    #从命令行获取传入参数
    # Bus_id = "b1000"
    # ip = "127.0.0.1"
    # port = 20001
    userroute3.register_blueprint(route3)
    userroute3.register_blueprint(confirm3)
    userroute3.run(host='127.0.0.1', port=20003, debug=True)