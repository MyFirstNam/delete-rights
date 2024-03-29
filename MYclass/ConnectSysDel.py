import datetime
import socket
import json
import  requests
def print_with_timestamp(message):
    current_time = datetime.datetime.now()
    timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

class ConnectSysDel:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def buildDelIns(self, delNotice):
        """
        生成删除指令
        :param delNotice:
        :return: delInstruction
        """
        delInstruction = {
            "affairs_id": delNotice["affairs_id"],
            "user_id": delNotice["user_id"],
            "info_id": delNotice["info_id"],      #把info_id改成infoID
            "deleteMethod": delNotice["deleteMethod"],
            "deleteGranularity": delNotice["deleteGranularity"], # 删除粒度；
            "deleteNotifyTree": delNotice["deleteNotifyTree"]
        }

        return delInstruction

    def sendDelIns(self, delInstruction):
        """
        发送删除指令
        :param delInstruction:{
        string affairs_id;
        string user_id;
        string info_id;
        "deleteMethod": "软件删除",
        string deleteGranularity; // 删除粒度；举例：age
        }
        :return:
        """
        delInstruction = {
            "systemID": 0x40000000,
            "systemIP": socket.gethostbyname(socket.gethostname()),
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data": delInstruction,
            "dataHash": "56e3be093f377b9d984eef02a982d852d1bce062fdb505bcf87df46141fd80aa"
        }

        # delInstruction = json.dumps(delInstruction)  把这一行删掉
        # url = f"http://{self.ip}:{self.port}/getInstruction"  # 替换为自己的实际目标URL
        # response = requests.post(url, json=delInstruction)
        # # 检查响应
        # if response.status_code == 200:
        #     print("POST请求成功")
        #     print("响应内容:", response.text)
        # else:
        #     print("POST请求失败")
        #     print("响应状态码:", response.status_code)
        return "已经成功给确定性删除系统发送删除指令！"


# 如下代码是与确定性删除系统对接的接口
# if __name__== "__main__":
#     delNotice = {
#         "affairs_id": "123",
#         "user_id": "123",
#         "info_id": "0c1d2e3f4g5h",
#         "from_bus_id": "123",
#         "to_bus_id": "123",  # 实现过程中，此参数应该是一个字符串，表示后续发送给某一个节点，在生成删除通知时需要根据情况更新
#         "deleteMethod": "123",
#         "deleteGranularity": "123",
#         "deleteNotifyTree": "123"  # 一个JSON
#     }
#     ip = "192.168.43.65"
#     port = 5000
#     Con = ConnectSysDel(ip, port)
#     instr = Con.buildDelIns(delNotice)
#     Con.sendDelIns(instr)
