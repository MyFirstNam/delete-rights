"""
py文件说明:
database_create
根据输入的参数创建指定数据库名字的数据库
"""

import mysql.connector
from mysql.connector import Error
import logging
from NodeSimulation.DAO.is_database_exists import is_database_exists


def database_create(host, user, password, port, database_name):
    """
    创建一个新的 MySQL 数据库。

    Parameters:
    host (str): 数据库服务器的主机名或 IP 地址。
    user (str): 用于连接数据库的用户名。
    password (str): 用于连接数据库的密码。
    port (int): 数据库服务器的端口号。
    database_name (str): 要创建的数据库的名称。

    Returns:
    bool: 操作成功返回 True，失败返回 False。
    """
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            port=port,
            charset='utf8mb4'
        )

        # 使用 with 语句管理游标资源
        # 使用 with 语句来确保游标在使用后正确关闭
        with connection.cursor() as cursor:
            # 新建数据库的 SQL 语句
            create_database_query = f"CREATE DATABASE IF NOT EXISTS {database_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            # 执行 SQL 语句
            cursor.execute(create_database_query)
            # 提交事务
            connection.commit()

        return True

    except Error as e:
        logging.error(f"Error occurred: {e}")
        return False

    finally:
        # 确保连接被关闭
        if connection.is_connected():
            connection.close()


# 函数功能测试

# host = "localhost"
# user = "root"
# password = "123456"
# port = 3306
# database = "business_b5555"
# #
# if is_database_exists(host, user, password, port, database):
#     logging.info("企业本地存证数据库已经存在")
# else:
#     logging.info(f"企业数据库不存在,正在新建数据库")
#     database_create(host, user, password, port, database)
#     logging.info(f"企业本地存证数据库新建成功，数据库名为{database}")
