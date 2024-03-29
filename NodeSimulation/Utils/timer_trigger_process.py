# 处理计时触发函数
# 对应删除计时管理与触发模块

import time


def time_tri_pro(delintention, time_limit, bus_id):
    """
    工作原理：
    具体的事件处理函数在解析数据包后，判定结果为计时触发
    之后会启动新线程进行计时，新的线程中会调用此函数进行计时
    计时结束后，此函数会更新删除意图(delintention)中对应的时间限制字段(time_limit)
    更新之后，给自己的监听路发送post请求进行处理
    todo 此外，此函数中还会把当前信息首先存储到数据库中，作为日志信息，因为计时信息，在计时结束以后就不会有计时信息了，必须提前存储
    此种处理方式：
    等价于计时触发函数负责计时，计时结束之后会处理为按需触发进行执行
    todo 另外一种办法，就是模拟回调函数，把后续的流程全部再执行一边，充代码量
    :param delintention: 删除意图
    :param time_limit: 时间限制
    :param bus_id: 节点ID，用于后续查找数据库，根据Bus_id查找
    :return: 无返回值，只执行发送post的操作
    """

    # 这里执行长时间运行的操作
    # sleep(30)
    #
    # url = f"http://127.0.0.1:10000/do_something"
    # # 要发送的数据
    # data = {
    #     "key1": "value1",
    #     "key2": "value2",
    #     'need_timing': "100"
    # }
    #
    # # 发送 POST 请求
    # response = requests.post(url, json=data)
    #
    # # 打印响应内容
    # print("Status Code:", response.status_code)
    # print("Response Body:", response.text)
    # print("正在计时")
    # time.sleep(10)
    print("计时删除触发正在处理!")
    time.sleep(10)
    print("计时处理结束")



