import mysql.connector


def is_database_exists(host, user, password, database):
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
        return False
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()


def database_create(host, user, password, port, database_name):
    connection = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        port=port,
        charset='utf8mb4'
    )

    # 创建一个游标对象
    cursor = connection.cursor()
    # 新建数据库的 SQL 语句
    create_database_query = f"CREATE DATABASE {database_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
    # 执行 SQL 语句
    cursor.execute(create_database_query)
    # 关闭游标和连接
    cursor.close()
    connection.close()

# # 示例用法
# host= "localhost"
# user= "root"
# password="123456"
# database = "test_mysql"
# if is_database_exists(host, user, password, database):
#     print("数据库存在")
# else:
#     print("数据库不存在")


# import mysql.connector
#
# # 连接 MySQL 服务器
# connection = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     password="123456"
# )
#
# # 创建一个游标对象
# cursor = connection.cursor()
# # # processor = InfoMemory(host="localhost", user="root", port=3306, password="123456", database="project26")
# # # processor = InfoMemory(host="10.170.42.45", port=3306, user="myuser", password="mypassword", database="project26")
# # # processor.insert_record(delNotice["user_id"], delNotice["info_id"],delNotice["deleteMethod"],delNotice["deleteGranularity"],delNotice["deleteNotifyTree"],triggerType,Bus_id,Timememory,Countmemory)
# # 新建数据库的 SQL 语句
# database_name = "test_mysql"
# create_database_query = f"CREATE DATABASE {database_name}"
#
# # 执行 SQL 语句
# cursor.execute(create_database_query)
#
# # 关闭游标和连接
# cursor.close()
# connection.close()
