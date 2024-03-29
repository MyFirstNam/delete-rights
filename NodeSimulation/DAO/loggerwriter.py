"""
py文件说明：
本类为对数据库的操作类，具体包括：
1.初始化，确保数据库连接无误，确保数据库中信息表存在
2.写入日志信息函数
3.更新日志信息函数
（更新是指，在流程操作过程中，后续产生新的日志信息，插入到旧条目中）
"""
import pymysql
import logging
from NodeSimulation.DAO.db_management import DatabaseManagement


class LoggerWriter:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def __init__(self, host, port, user, password, database, table_name):
        """
        初始化方法，用于设置数据库连接并检查指定的表是否存在。

        参数:
        host (str): 数据库服务器的主机名或 IP 地址。
        port (int): 数据库服务器的端口号。
        user (str): 用于连接数据库的用户名。
        password (str): 用户的密码。
        database (str): 要连接的数据库名称。
        table_name (str): 需要检查的表名。
        """
        # 后续在插入数据时，需要用到表名
        self.__table_name = table_name

        # 创建数据库管理器实例
        self.db_manager = DatabaseManagement(host, port, user, password, database)
        connect = self.db_manager.get_connection()
        try:
            # 检查指定的表是否已存在
            if self.db_manager.table_exists(connect, self.__table_name):
                logging.info(f"本节点中的信息日志记录存储数据表 {self.__table_name} 存在")
            else:
                # 如果表不存在，创建新表
                # logging.info(f"本节点中的信息日志记录存储数据表 {table_name} 不存在，正在创建...")
                self.db_manager.create_table(connect, self.__table_name)
        except Exception as e:
            # 捕获并记录任何异常
            logging.error(f"检查或创建表时发生错误: {e}")

    def intention_record(self, AffairsID, InfoID, IsRoot, UserID, DeleteMethod, DeleteGranularity, TriggerType,
                         SourceDomain):
        """
        TODO 按需删除触发将特定日志数据插入到数据库，存储内容为参数内容
        服务于按需删除
        参数:
        AffairsID - 事务ID
        InfoID - 信息ID
        IsRoot - 是否为根节点
        UserID - 用户ID
        DeleteMethod - 删除方法
        DeleteGranularity - 删除粒度
        TriggerType - 触发类型
        SourceDomain - 源域
        返回:
        无。直接将数据插入数据库并记录相关日志。
        """

        # 初始化数据库连接为None
        conn = None
        try:
            # 尝试从db_manager获取数据库连接
            conn = self.db_manager.get_connection()
            # 如果连接失败（即返回None），抛出异常
            if conn is None:
                raise Exception("数据库连接失败")

            # 使用with语句确保使用后关闭数据库游标
            with conn.cursor() as cursor:
                # 准备要执行的SQL插入语句
                sql = f"INSERT INTO `{self.__table_name}` (AffairsID, InfoID, IsRoot, UserID, DeleteMethod, DeleteGranularity, TriggerType, SourceDomain) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
                # 执行SQL语句并传入参数
                cursor.execute(sql, (AffairsID, InfoID, IsRoot, UserID, DeleteMethod, DeleteGranularity, TriggerType, SourceDomain))
                # 提交事务
                conn.commit()
                # 记录成功插入的日志
                logging.info("当前日志信息存储成功！！！！")

        except Exception as e:
            # 如果在尝试插入数据时发生异常，记录错误日志
            logging.error(f"存储日志信息时发生错误: {e}")
            # 如果数据库连接仍然打开，则回滚更改
            if conn:
                conn.rollback()

        finally:
            # 最后，无论成功或失败，确保关闭数据库连接
            if conn:
                conn.close()

    def count_record(self, AffairsID, InfoID, IsRoot, UserID, DeleteMethod, DeleteGranularity, TriggerType,
                         SourceDomain, CountLimit):
        """
        TODO 计次删除触发将特定日志数据插入到数据库，存储内容为参数内容
        服务于按需删除
        参数:
        AffairsID - 事务ID
        InfoID - 信息ID
        IsRoot - 是否为根节点
        UserID - 用户ID
        DeleteMethod - 删除方法
        DeleteGranularity - 删除粒度
        TriggerType - 触发类型
        SourceDomain - 源域
        CountLimit - 次数限制
        返回:
        无。直接将数据插入数据库并记录相关日志。
        """

        # 初始化数据库连接为None
        conn = None
        try:
            # 尝试从db_manager获取数据库连接
            conn = self.db_manager.get_connection()
            # 如果连接失败（即返回None），抛出异常
            if conn is None:
                raise Exception("数据库连接失败")

            # 使用with语句确保使用后关闭数据库游标
            with conn.cursor() as cursor:
                # 准备要执行的SQL插入语句
                sql = f"INSERT INTO `{self.__table_name}` (AffairsID, InfoID, IsRoot, UserID, DeleteMethod, DeleteGranularity, TriggerType, SourceDomain, CountLimit) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                # 执行SQL语句并传入参数
                cursor.execute(sql, (AffairsID, InfoID, IsRoot, UserID, DeleteMethod, DeleteGranularity, TriggerType, SourceDomain, CountLimit))
                # 提交事务
                conn.commit()
                # 记录成功插入的日志
                logging.info("当前日志信息存储成功！！！！")

        except Exception as e:
            # 如果在尝试插入数据时发生异常，记录错误日志
            logging.error(f"存储日志信息时发生错误: {e}")
            # 如果数据库连接仍然打开，则回滚更改
            if conn:
                conn.rollback()

        finally:
            # 最后，无论成功或失败，确保关闭数据库连接
            if conn:
                conn.close()


    def read(self, query):
        # 实现读取数据的逻辑
        pass

    def update(self, data):
        # 实现更新数据的逻辑
        pass

    def delete(self, identifier):
        # 实现删除数据的逻辑
        pass

    def close_connection(self):
        # 关闭数据库连接
        self.conn.close()


# 类功能函数测试
# host = "localhost"
# user = "root"
# password = "123456"
# port = 3306
# database = "business_b5555"
# table_name = "testb5555"
#
# # 初始化功能测试
# db_test = LoggerWriter(host, port, user, password, database, table_name)
#
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
# # intention_record函数测试
# # 删除意图按需删除日志信息存储
# # db_test.intention_record(delintention["affairs_id"], delintention["info_id"], True, delintention["user_id"], delintention["deleteMethod"], delintention["deleteGranularity"], "按需触发", delintention["source_bus_id"])
#
# # count_record函数测试
# # 删除意图计次删除日志信息存储
# db_test.count_record(delintention["affairs_id"], delintention["info_id"], True, delintention["user_id"], delintention["deleteMethod"], delintention["deleteGranularity"], "计次触发", delintention["source_bus_id"], 10)