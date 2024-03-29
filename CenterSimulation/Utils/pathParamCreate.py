import socket
import datetime


def path_request_create(globalID, affairsID):
    """
    组成信息流转路径请求内容
    :param self:
    :param globalID:
    :param affairsID:
    :return:
    """
    pathdata = {
        "globalID": globalID
    }
    pathreq = {
        "systemID": 0x40000000,
        "systemIP": socket.gethostbyname(socket.gethostname()),
        "evidenceID": globalID + affairsID,
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data": pathdata,
        "dataHash": "56e3be093f377b9d984eef02a982d852d1bce062fdb505bcf87df46141fd80aa"
    }

    return pathreq


# 测试
if __name__ == '__main__':
    globalID = "asdffa"
    affairsID = "123445"
    pathreq = path_request_create(globalID, affairsID)
    print(pathreq)