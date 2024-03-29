import json
import struct
import socket
import datetime
from MYclass.InfoMemory import InfoMemory
import pprint

class CenterMemory:
    def __init__(self, AffairsID, InfoID):
        # self.UserId = UserId
        self.AffairsID = AffairsID
        self.InfoID = InfoID

    def create_packet(self, version: int, command_type: int, affair_type: int, message_version: int, enc_mode: int, auth_mode: int, save_field: int, payload: str):
        """
        :param version:版本号
        :param command_type:命令类型
        :param affair_type:事务类型
        :param message_version:消息版本
        :param enc_mode:加密模式
        :param auth_mode:认证模式
        :param save_field:保存字段
        :param payload:负载
        :return:
        """
        payload = payload.encode("utf8")

        # 组装头部
        #struct.pack('>I', version)[2:]：这一部分将整数 version 转换为大端（Big-endian）字节序的4字节无符号整数，并且取该字节流的后两个字节（2个字节）。这样做是因为可能只希望使用这4字节中的一部分，所以通过 [2:] 来截取字节流的后两个字节
        length = 18 + len(payload) + 16
        head = struct.pack('>I',version)[2:] + struct.pack('>I',command_type)[2:] + struct.pack('>I',affair_type)[2:] + \
                 struct.pack('>I',message_version)[2:] + struct.pack('>I',enc_mode)[3:] + struct.pack('>I',auth_mode)[3:] + \
                 struct.pack('>I',save_field) + struct.pack('>I',length)

        # 认证与校验域 16字节
        tail = b"\00" * 16
        return head + payload + tail

    # 存证信息上报请求
    def send_message(self, ip1:str,port1:int,ip2:str,port2:int,data1:bytes):
        """
        :param ip: 目标IP
        :param port: 目标端口号
        :param data1: 发送存证信息请求
        :param data2: 存证信息上报
        :return:
        """
        # 创建一个基于IPv4和TCP协议的客户端套接字对象，用于与远程服务器建立连接并进行数据传输
        client_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket1.connect((ip1, port1))

        # 发送存证信息请求
        client_socket1.sendall(data1)
        print("数据发送成功")

        # 接收 请求应答
        recv_data1 = client_socket1.recv(1024)
        json_recv1 = recv_data1[18:][:-16].decode()
        print(f"第一次接收json数据:{json_recv1}")
        # 将jsonn转为字典格式
        json_recv1 = json.loads(json_recv1)
        # 关闭第一次通信
        client_socket1.close()
        # 组织第二次json数据


        processor = InfoMemory(host="localhost", user="root", port=3306, password="123456", database="business_b1000")
        # todo 这里的UserID和infoID之后需要换成参入的参数
        data = processor.searchinfoall(self.AffairsID, self.InfoID)

        title = "企业节点对信息" + data[0][2] + "进行删除通知"
        abstract = "企业节点" + data[0][8] + "通过" + data[0][7] + "接受" + "用户" + data[0][
            1] + "删除" + self.InfoID + "信息的请求,进行删除通知,通知完成"
        deleteIntention = data[0][1] + "请求删除其身份证信息"

        memorydata = {
            "systemID": 0x40000000,
            "systemIP": socket.gethostbyname(socket.gethostname()),
            "mainCMD": 0x0003,
            "subCMD": 0x0040,
            "evidenceID": "00032dab40af0c56d2fa332a4924d150",
            "msgVersion": 0x4010,
            "submittime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data": {
                "globalID": self.InfoID,
                "title": title,
                "status": "已通知",
                "abstract": abstract,
                "keyWords": "删除通知",
                "category": "4-1-1",
                "userID": data[0][1],
                # "infoID": self.InfoID,
                "deleteGranularity": data[0][4],
                "deleteIntention": deleteIntention,
                "deleteTriggers": data[0][7],
                "deleteConfirmation": "200",
                "deleteMethod": data[0][3],
                "deleteNotifyTree": data[0][5],
               # "delConfirmSignatureDict": data[0][6]
                "delConfirmSignatureDict": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
            },
            "dataHash": "56e3be093f377b9d984eef02a982d852d1bce062fdb505bcf87df46141fd80aa",
            "datasign": "56e3be093f377b9d984eef02a982d852d1bce062fdb505bcf87df46141fd80aa",
            "randomidentification": json_recv1["randomidentification"]
        }


        json2 = json.dumps(memorydata, indent=4)
        data2 = self.create_packet(0x0001, 0x0003, 0x0040, 0x4010, 0x0, 0x0, 0x0, json2)

        print("第二次发送数据：",data2[18:][:-16].decode())
        # 建立第二次socket通信
        client_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket2.connect((ip2, port2))

        # 发送存证信息上报
        client_socket2.sendall(data2)

        # 接收存证信息回复
        recv_data2 = client_socket2.recv(1024)
        # print(recv_data2)
        # print(recv_data2[18:][:-16])
        json_recv2 = recv_data2[18:][:-16].decode("utf8")
        print(f"第二次接收json数据:{json_recv2}")

        # 关闭套接字连接
        client_socket2.close()


if __name__ == '__main__':

    # 第一次的json
    json1 = json.dumps({
        "systemID": 0x40000000,
        "systemIP": socket.gethostbyname(socket.gethostname()),
        "mainCMD": 0x0001,
        "subCMD": 0x0020,
        "evidenceID": "00032dab40af0c56d2fa332a4924d150",
        "msgVersion": 0x1000,
        "reqtime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data": {
            "objectSize": 0,
            "objectMode": ""        #把字符串置空
        },
        "datasign": "56e3be093f377b9d984eef02a982d852d1bce062fdb505bcf87df46141fd80aa"
    }, indent=4)
    center = CenterMemory("16881233","0c1d2e3f4g5h")
    # 第一次请求
    data1 = center.create_packet(0x0001, 0x0001, 0x0040, 0x4000, 0x0, 0x0, 0x0, json1)
    center.send_message("124.127.245.34",50005,"124.127.245.34",50004, data1)



    #send_message("localhost", 50010, "localhost", 50004, data1)

    # processor = InfoMemory(host="localhost", user="root", port=3306, password="123456", database="business_b1000")
    # # todo 这里的UserID和infoID之后需要换成参入的参数
    # data = processor.searchinfoall("0001", "0x0002")
    #
    # title = "企业节点对信息" + data[0][2] + "进行删除通知"
    # abstract = "企业节点" + data[0][8] + "通过" + data[0][7] + "接受" + "用户" + data[0][
    #     1] + "删除" + "0x0002" + "信息的请求,进行删除通知,通知完成"
    # deleteIntention = data[0][1] + "请求删除其身份证信息"
    #
    # memorydata = {
    #     "systemID": 0x40000000,
    #     "systemIP": socket.gethostbyname(socket.gethostname()),
    #     "mainCMD": 0x0003,
    #     "subCMD": 0x0040,
    #     "evidenceID": "00032dab40af0c56d2fa332a4924d150",
    #     "msgVersion": 0x4010,
    #     "submittime": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    #     "data": {
    #         "globalID": "时间戳+随机数+产生信息系统名字",
    #         "title": title,
    #         "abstract": abstract,
    #         "keyWords": "删除通知",
    #         "category": "4-1-1",
    #         "userID": data[0][1],
    #         "infoID": "0x0002",
    #         "deleteGranularity": data[0][4],
    #         "deleteIntention": deleteIntention,
    #         "deleteTriggers": data[0][7],
    #         "deleteConfirmation": "200",
    #         "deleteMethod": data[0][3],
    #         "deleteNotifyTree": data[0][5],
    #         "delConfirmSignatureDict": data[0][6]
    #     },
    #     "dataHash": "56e3be093f377b9d984eef02a982d852d1bce062fdb505bcf87df46141fd80aa",
    #     "datasign": "56e3be093f377b9d984eef02a982d852d1bce062fdb505bcf87df46141fd80aa",
    # }
    # pprint.pprint(memorydata)