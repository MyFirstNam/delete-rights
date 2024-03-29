"""
此py文件定义"代理"中心机构事务处理类：
类中包含的函数的具体功能：
    1.删除通知异常 / 删除通知确认异常协助转发
    2.删除通知日志协助转发
    3
"""


class LoggingForward:

    def __init__(self):
        pass

    def exceptionforward(self, exceptionInfo):
        """
        函数说明，协助组成完整的上报的异常信息,因为接收到的信息是系统内部的信息，不完全符合课题一的要求
        按照既定的协议格式进行转发
        :param exceptionInfo:系统内部上报的异常信息内容
        :return:
        """
        # 首先判断是删除通知异常，还是删除通知确认异常




        pass

    def loggingforward(self, loggingInfo):
        """
        函数说明，协助组成完整的上报的日志信息,因为接收到的信息是系统内部的信息，不完全符合课题一的要求
        按照既定的协议格式进行转发
        :param loggingInfo:系统内部上报的异常信息内容
        :return:
        """
        pass

