"""
py文件说明
此文件为处理与数据库相关的内容，具体包括：
1.连接数据库
2.断开数据库连接
3.判断指定的表是否存在
4.新建数据表函数
5.删除数据表函数
"""

import pymysql
import logging
from pymysql import Error


class DatabaseManagement:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def __init__(self, host: str, port: int, user: str, password: str, database: str) -> None:
        """
        初始化数据库连接。

        参数:
        host (str): 数据库服务器的主机名或 IP 地址。
        port (int): 数据库服务器的端口号。
        user (str): 用于连接数据库的用户名。
        password (str): 用户的密码。
        database (str): 要连接的数据库名称。

        """
        self.__host = host
        self.__port = port
        self.__user = user
        self.__passwd = password
        self.__database = database
        self.conn = None

    def get_connection(self):
        """
        获取数据库连接对象。
        如果连接对象尚未创建或已关闭，将尝试创建一个新的数据库连接。
        返回:
        pymysql.connections.Connection or None: 数据库连接对象或 None（如果连接失败）。
        """
        if self.conn is None:
            try:
                self.conn = pymysql.connect(
                    host=self.__host,
                    port=self.__port,
                    user=self.__user,
                    password=self.__passwd,
                    database=self.__database,
                )
                logging.info(f"{self.__database}数据库连接成功！")

            except pymysql.Error as e:
                logging.error(f"连接到数据库 {self.__database} 失败: {e}")
                self.conn = None  # 确保连接对象被设置为 None
        return self.conn

    def table_exists(self, connect, table_name):
        """
        检查指定的表是否在数据库中存在。
        参数:
        connect (pymysql.connections.Connection): 数据库连接对象。
        table_name (str): 需要检查的表名。
        返回:
        bool: 如果表存在返回 True，否则返回 False。
        """
        if not isinstance(table_name, str):
            logging.error(f"提供的数据表名不是一个有效的字符串: {table_name},查询失败！！！")
            return True

        # 创建一个新的游标对象用于执行查询
        cursor = connect.cursor()
        try:
            # 执行 SQL 查询来获取所有表的名称
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()

            # 提取表名列表
            table_list = [table[0] for table in tables]
        finally:
            # 无论查询结果如何，确保游标被关闭
            cursor.close()

        # 检查指定的表名是否在提取的表名列表中
        # 表存在返回True，不存在返回 False
        return table_name in table_list

    def create_table(self, connect, database_name):
        """
        创建指定的表在数据库中。
        参数:
        connect (pymysql.connections.Connection): 数据库连接对象。
        database_name (str): 需要创建的表名。
        返回:
        如果表名有误返回 True，否则创建数据表不返回值。
        """
        # 检查 database_name 是否是字符串
        if not isinstance(database_name, str):
            logging.error(f"提供的数据表名不是一个有效的字符串: {database_name}, 创建失败！！！")
            return

        logging.info(f"本节点中的信息日志记录存储数据表 {database_name} 不存在，正在创建...")
        cursor = connect.cursor()
        try:
            create_table_query = f"""
            CREATE TABLE `{database_name}` (
                AffairsID VARCHAR(255),
                InfoID VARCHAR(255),
                IsRoot BOOLEAN,
                UserID VARCHAR(255),
                DeleteMethod VARCHAR(255),
                DeleteGranularity VARCHAR(255),
                DeleteNotifyTree TEXT,
                DelConfirmSignatureDict TEXT,
                TriggerType VARCHAR(255),
                SourceDomain VARCHAR(255),
                TimeLimit VARCHAR(255) DEFAULT "",
                CountLimit INT DEFAULT 0,
                submittime DATETIME
            )
            """
            #  PRIMARY KEY(AffairsID, InfoID)
            # TODO 测试过程中中为了简易，没有设置主键
            cursor.execute(create_table_query)
            connect.commit()
            logging.info(f"本节点中的信息日志记录存储数据表 {database_name} 创建成功！")
        except Exception as e:
            logging.error(f"创建数据表 {database_name} 失败: {e}")
        finally:
            cursor.close()

    def drop_table(self, connect, table_name):
        """
        删除指定的数据库表。
        参数:
        connect (pymysql.connections.Connection): 数据库连接对象。
        table_name (str): 要删除的表名。
        返回:
        无实际返回值
        """
        # 检查表名是否有效
        if not isinstance(table_name, str):
            logging.error(f"提供了无效的表名: {table_name}")
            return

        try:
            with connect.cursor() as cursor:
                # SQL 语句删除表
                drop_table_query = f"DROP TABLE IF EXISTS `{table_name}`"
                cursor.execute(drop_table_query)
                connect.commit()
                logging.error(f"表 {table_name} 已被删除")
        except Error as e:
            logging.error(f"删除表 {table_name} 时发生错误: {e}")


# 类功能函数测试
# host = "localhost"
# user = "root"
# password = "123456"
# port = 3306
# database = "business_b5555"
# table_name = "testb5555"
#
# db_manager = DatabaseManagement(host, port, user, password, database)
# connect = db_manager.get_connection()

# # 测试创建表函数与表存在函数
# if db_manager.table_exists(connect, table_name):
#     logging.info("数据表存在")
# else:
#     logging.info("数据表不存在")
#     db_manager.create_table(connect, table_name)

# 测试表删除函数
# if db_manager.table_exists(connect, table_name):
#     logging.info("数据表存在")
#     db_manager.drop_table(connect, table_name)
#     logging.info("数据表删除成功")
# else:
#     logging.info("数据表不存在")
#     db_manager.create_table(connect, table_name)
