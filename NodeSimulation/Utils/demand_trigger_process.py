# 处理按需触发函数
# 按需触发就是直接触发，没有计时，计时
# 对应按需触发删除模块

import configparser
import logging
import os

from NodeSimulation.DAO.is_database_exists import is_database_exists
from NodeSimulation.DAO.create_database import database_create
from NodeSimulation.DAO.loggerwriter import LoggerWriter


def demand_tri_pro(delintention, bus_id):
    """工作原理：
    具体的事件处理函数在解析数据包后，判定结果为按需触发
    但是当删除指令通知与确认系统接收到请求删除的数据包时，表明计次已经结束，开始删除通知等后续操作

    此函数的功能：
        1.解析按需删除意图，生成删除请求
        2.存储当前信息，对于按需触发，没有计时/计次等特殊字段，但是为了整体结构统一，还是进行存储
        # todo 为了防止此次存储中覆盖了数据库中已经存储好的计时信息，所以不对“时间限制，次数限制”字段进行存储，也不“更新”这个两列
    :param  delintention: 删除意图
            delintention = {
            "affairs_id": "00001",
            "user_id": "u00001",
            "deleteGranularity": "硬件删除",
            "info_id": "a1b2c3d4e5",
            "source_bus_id": "b00001",
            "time_limit": "",  # 时间限制为可选字段，不是每次内容都有，""空字符表示没有时间显示
            "count_limit": 0,  # 次数限制为可选字段，不是每次内容都有，0表示没有次数限制
            "deleteMethod": "硬件删除"
            }
    :param bus_id: 节点ID，用于 34 后续查找数据库，根据Bus_id查找
    :return: delrequest: 删除请求
             delrequest = {
            "affairs_id": "00001",
            "user_id": "u00001",
            "info_id": "a1b2c3d4e5",
            "deleteMethod": "硬件删除",
            "deleteGranularity": "硬件删除"
            }
    """

    # 生成删除请求
    delrequest = {
        "affairs_id": delintention["affairs_id"],
        "user_id": delintention["user_id"],
        "info_id": delintention["info_id"],
        "deleteMethod": delintention["deleteMethod"],
        "deleteGranularity": delintention["deleteGranularity"]
    }

    # 设置按需删除独有的特征值
    IsRoot = True
    TriggerType = "按需触发"

    # 开始当前日志信息存储
    # 创建ConfigParser对象，用于解析配置文件
    config = configparser.ConfigParser()

    try:
        # 获取当前文件的绝对路径
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # 设置相对于当前文件的路径
        config_folder = os.path.join(current_dir, '..', 'Resource')
        config_file = 'dbconfig.ini'

        # 组合并规范化路径
        config_path = os.path.normpath(os.path.join(config_folder, config_file))

        # 读取配置文件
        config.read(config_path)

        # 从配置文件中获取数据库连接参数
        host = config.get('Database', 'host')
        user = config.get('Database', 'user')
        password = config.get('Database', 'password')
        port = config.getint('Database', 'port')
        database = config.get('Database', 'database')
        # 在数据库名后加上bus_id以区分不同的数据库
        database += bus_id
        table_name = config.get('Database', 'table_name')
        # 在表名后加上bus_id以区分不同的信息表
        table_name += bus_id

        # 检查数据库是否已经存在
        if is_database_exists(host, user, password, port, database):
            # 如果数据库存在，则记录日志并继续执行数据存储操作
            logging.info("企业本地日志存证数据库已经存在，对删除日志信息正在本地存证···")
            # 创建LoggerWriter实例，准备写入日志
            loggingwriter = LoggerWriter(host, port, user, password, database, table_name)
            # 记录删除意图数据
            loggingwriter.intention_record(delintention["affairs_id"], delintention["info_id"], IsRoot,
                                           delintention["user_id"], delintention["deleteMethod"],
                                           delintention["deleteGranularity"], TriggerType,
                                           delintention["source_bus_id"])

        else:
            # 如果数据库不存在，先创建数据库，然后记录日志并存储数据
            logging.info(f"企业数据库不存在，正在新建数据库···数据库名为{database}")
            database_create(host, user, password, port, database)
            logging.info(f"企业本地日志存证数据库新建成功，数据库名为{database}")
            # 创建LoggerWriter实例，准备写入日志
            loggingwriter = LoggerWriter(host, port, user, password, database, table_name)
            # 记录删除意图数据
            loggingwriter.intention_record(delintention["affairs_id"], delintention["info_id"], IsRoot,
                                           delintention["user_id"], delintention["deleteMethod"],
                                           delintention["deleteGranularity"], TriggerType,
                                           delintention["source_bus_id"])

    except configparser.Error as e:
        # 捕获并记录解析配置文件时的错误
        logging.error(f"读取配置文件时发生错误: {e}")
    except KeyError as e:
        # 捕获并记录配置项缺失的错误
        logging.error(f"配置项缺失: {e}")

    return delrequest


# 函数功能测试

# delintention = {
#     "affairs_id": "00001",
#     "user_id": "u00001",
#     "deleteGranularity": "硬件删除",
#     "info_id": "a1b2c3d4e5",
#     "source_bus_id": "b00001",
#     "time_limit": "",  # 时间限制为可选字段，不是每次内容都有，""空字符表示没有时间显示
#     "count_limit": 0,  # 次数限制为可选字段，不是每次内容都有，0表示没有次数限制
#     "deleteMethod": "硬件删除"
# }
#
# db = demand_tri_pro(delintention, "b5555")
