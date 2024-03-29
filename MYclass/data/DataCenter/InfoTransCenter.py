#import mysql.connector
import json
import re
import pymysql
import requests
import csv

class InfoTransCenter:
    def __init__(self, host: str, port: int, user: str, password: str, database: str) -> None:
        self.__host = host
        self.__port = port
        self.__user = user
        self.__passwd = password
        self.__database = database
        self.__conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
        )
        print("[info] The connection to the database start")

    def __del__(self):
        print("[info] The connection to the database is closed")
        self.__conn.close()

    def __table_exists(self,table_name):
        cursor = self.__conn.cursor()
        # 查询是否存在该表
        sql = "show tables;"
        cursor.execute(sql)
        tables = [cursor.fetchall()]
        table_list = re.findall('(\'.*?\')', str(tables))
        table_list = [re.sub("'", '', each) for each in table_list]
        if table_name in table_list:
            # 存在返回1
            return 1
        else:
            # 不存在返回0
            return 0

    # 信息第一次流转，调用此函数，建立information表，存储流转次数
    def delete_info(self,affairs_id:str,info_id:str,user_id:str,deleteGranularity:str,source_bus_id:str,count_limit:int,deleteMethod:str):
        cursor = self.__conn.cursor()
        # 查询数据库中是否存在表
        if not self.__table_exists("information"):
            # 如果表不存在，创建名表
            print(f"[info] table for information has been cteated!")
            create_table_query = f"""
            CREATE TABLE `information` (
                affairs_id VARCHAR(255),
                info_id VARCHAR(255),
                user_id VARCHAR(255),
                deleteGranularity VARCHAR(255),
                source_bus_id VARCHAR(255),
                count_limit INT,
                deleteMethod VARCHAR(255)
            ) 
            """
            cursor.execute(create_table_query)
            print(f"[info] Table information has been created!")
            self.__conn.commit()

        # 执行插入操作
        insert_query = f"INSERT INTO `information` (affairs_id,info_id,user_id,deleteGranularity,source_bus_id,count_limit,deleteMethod) VALUES (%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(insert_query, (affairs_id,info_id,user_id,deleteGranularity,source_bus_id,count_limit,deleteMethod))
        print(f"[info] TransData from INFORMATION has been inserted!")

    def insert_record(self,info_id:str,from_bus_id:str, to_bus_id:str):
        cursor = self.__conn.cursor()
        # 查询数据库中是否存在表
        if not self.__table_exists(info_id):
        # 如果表不存在，创建名表
            print(f"[info] table for {info_id} has been cteated!")
            create_table_query = f"""
            CREATE TABLE `{info_id}` (
                from_bus_id VARCHAR(255),
                to_bus_id VARCHAR(255)
            ) 
            """
            cursor.execute(create_table_query)
            print(f"[info] Table {info_id} has been created!")
            self.__conn.commit()

        count_query = f"SELECT COUNT(*) FROM `{info_id}`"
        cursor.execute(count_query)
        count = cursor.fetchone()[0]
        print(f"目前信息{info_id}中的流转次数是{count}")

        count_limit = "SELECT count_limit FROM {} WHERE  info_id = %s ".format("information")
        cursor.execute(count_limit, info_id)
        results = cursor.fetchone()

        if count < results[0]:
            # 执行插入操作
            insert_query = f"INSERT INTO `{info_id}` (from_bus_id, to_bus_id) VALUES (%s,%s)"
            cursor.execute(insert_query,(from_bus_id,to_bus_id))
            print(f"[info] TransData from {from_bus_id} to {to_bus_id} has been inserted!")
            cursor.close()
            self.__conn.commit()
            return
        else:
             print("数据流转次数达到最大限制，中心监管机构发起删除请求！")
             search_query = "SELECT * FROM {} WHERE  info_id = %s ".format("information")
             cursor.execute(search_query, info_id)
             results = cursor.fetchall()

             cursor.close()
             self.__conn.commit()
             delintention = {
                 "affairs_id": results[0][0],
                 "info_id": results[0][1],
                 "user_id": results[0][2],
                 "deleteGranularity": results[0][3],
                 "source_bus_id": results[0][4],
                 "count_limit": results[0][5],
                 "deleteMethod": results[0][6]
             }
             print(delintention)
             with open('../../ID.csv', 'r') as csvfile:
                 reader = csv.DictReader(csvfile)
                 for row in reader:
                     if row['ID'] == delintention["source_bus_id"]:  # 默认源企业节点的ID是b1000
                         port = row['port']
                         ip = row['IP']
             delintention = json.dumps(delintention)
             url = f"http://{ip}:{port}/test/postx/endpointx"  # 替换为自己的实际目标URL
             print(url)
             response = requests.post(url, json=delintention)
             # 检查响应
             if response.status_code == 200:
                 print("POST请求成功")
                 print(response.text)
             else:
                 print("POST请求失败")
                 print("响应状态码:", response.status_code)
             return


    def get_transfer_path(self, info_id):
        cursor = self.__conn.cursor()
        # 查询数据库中是否存在表
        if not self.__table_exists(info_id):
            print(f"[Error] No transfer_path for info_id:{info_id} can be found!")
            cursor.close()
            return

        # 执行查询操作
        query = f"SELECT * FROM `{info_id}`"
        cursor.execute(query)

        # 对得到结果进行包装
        '''
        {
        "infoID":"283749abaa234cde",
        "dataTransferPath": [
            { "from": "b1000", "to": "b1001" },
            { "from": "b1001", "to": "b1002" },
            { "from": "b1002", "to": "b1003" }
            ]

        }
        '''
        data = {
            "info_id":info_id,
            "dataTransferPath":[]
        }
        query_result = cursor.fetchall()
        for row in query_result:
            temp = {
                "from":row[0],
                "to":row[1]
            }
            data["dataTransferPath"].append(temp)

        # print(f"[info] The dataTransferPath for {info_id} is:{json.dumps(data)}")

        # 该表完成了使命，现在要对他删除了
        # print(f"[info] table for {info_id} has been destroyed!")
        # drop_table_query = f"DROP TABLE IF EXISTS `{info_id}`" # 确保table存在时才会执行删除！！，防止出错
        # cursor.execute(drop_table_query)
        # 提交结束
        cursor.close()
        self.__conn.commit()
        return data


if __name__ == "__main__":
    processor = InfoTransCenter(
        host = "localhost",
        user = "root",
        port = 3306,
        password = "123456",
        database = "centerInfo"
    )

    # processor = InfoTransCenter(
    #     host = "10.170.42.45",
    #     user = "myuser",
    #     port = 3306,
    #     password = "mypassword",
    #     database = "centerInfo"
    # )

    # 第一次数据流转
    # processor.delete_info("0001","0x00001","b00001","age", "b1000", 10,"软件删除")
    # processor.insert_record("0x00001","b1000","b1001")
    # 后续数据流转
    processor.insert_record("0x00001","b1001","b1002")
    # processor.insert_record("0x00001","b1002","b1003")


    # print(processor.get_transfer_path("0x00001"))