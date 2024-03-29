"""
py文件说明:
is_database_exist
根据参数中数据库名字判断特定数据库是否存在
"""

import mysql.connector
import logging


def is_database_exists(host, user, password, port, database):
    """
    Check if a specific database exists.

    Parameters:
    host (str): 数据库服务器的主机名或 IP 地址。
    user (str): 用于连接数据库的用户名。
    password (str): 用于连接数据库的密码。
    port (int): 数据库服务器的端口号。
    database (str): 要检查的数据库的名称。

    Returns:
    bool: True if the database exists, False otherwise.
    """
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4'
        )
        return True

    except mysql.connector.Error as err:
        logging.error(f"Error: {err}")
        return False

    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()


# 函数功能测试

# host = "localhost"
# user = "root"
# password = "123456"
# port = 3306
# database = "business"
#
# if is_database_exists(host, user, password, port, database):
#     logging.info("企业本地存证数据库已经存在")
# else:
#     logging.info(f"企业数据库不存在")
