import re
import pymysql
import datetime
def print_with_timestamp(message):
    current_time = datetime.datetime.now()
    timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

class InfoMemory:
    # 这个类服务于数据库，包括每个节点存证信息，与查询信息
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
        print_with_timestamp("数据库链接成功！！！")

    #     connection = pymysql.connect(**db_params)
    def __del__(self):
        # print("[info] The connection to the database is closed")
        self.__conn.close()

    def __table_exists(self, table_name):
        cursor = self.__conn.cursor()
        sql = "show tables;"
        cursor.execute(sql)
        tables = cursor.fetchall()
        table_list = [table[0] for table in tables]  # 直接获取表名
        cursor.close()  # 关闭游标
        if table_name in table_list:
            return 1
        else:
            return 0

    def insert_record(self,AffairsID,UserID,InfoID,DeleteMethod,DeleteGranularity,DeleteNotifyTree,triggerType,SourceDomain,TimeLimit,CountLimit):
        cursor = self.__conn.cursor()
        # 查询数据库中是否存在表
        if not self.__table_exists(self.__database):
            # 如果表不存在，创建名表
            print_with_timestamp(f"本企业中的信息记录存储数据表不存在，正在被创建···")
            create_table_query = f"""
			CREATE TABLE `{self.__database}` (
			    AffairsID VARCHAR(255),
				UserID VARCHAR(255),
				InfoID VARCHAR(255),
				DeleteMethod VARCHAR(255),
				DeleteGranularity VARCHAR(255),
				DeleteNotifyTree TEXT,
				DelConfirmSignatureDict TEXT,
				triggerType VARCHAR(255),
				SourceDomain VARCHAR(255),
				TimeLimit VARCHAR(255),
				CountLimit INT
			)
			"""
            cursor.execute(create_table_query)
            print_with_timestamp(f"本企业中的信息记录存储数据表创建成功！")
            self.__conn.commit()

        # 执行插入操作
        # 在插入数据之前设置字符集

        insert_query = f"INSERT INTO `{self.__database}` (AffairsID,UserID,InfoID,DeleteMethod,DeleteGranularity,DeleteNotifyTree,triggerType,SourceDomain,TimeLimit,CountLimit) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(insert_query, (AffairsID,UserID,InfoID,DeleteMethod,DeleteGranularity,DeleteNotifyTree,triggerType,SourceDomain,TimeLimit,CountLimit))
        # print(f"[info] TransData from {UserID} has been inserted!")

        cursor.close()
        self.__conn.commit()
    # # def insert_newrecord(self, UserID,DelConfirmSignatureDict):
    # #     cursor = self.__conn.cursor()
    # #     # 查询数据库中是否存在表
    # #     if not self.__table_exists(UserID):
    # #         # 如果表不存在，创建名表
    # #         print(f"[info] table for {UserID} has been cteated!")
    # #         create_table_query = f"""
    # #         CREATE TABLE `{UserID}` (
    # #             UserID VARCHAR(255),
    # #             InfoID VARCHAR(255),
    # #             DeleteMethod VARCHAR(255),
    # #             DeleteGranularity VARCHAR(255),
    # #             DeleteNotifyTree VARCHAR(255),
    # #             DelConfirmSignatureDict BLOB,
    # #             triggerType VARCHAR(255),
    # #             SourceDomain VARCHAR(255),
    # #             TimeLimit VARCHAR(255),
    # #             CountLimit INT
    # #         )
    # #         """
    # #         cursor.execute(create_table_query)
    # #         print(f"[info] Table {UserID} has been created!")
    # #         self.__conn.commit()
    # #
    # #     # 执行插入操作
    # #     update_query = f"UPDATE `{UserID}` SET DelConfirmSignatureDict = %s WHERE InfoID = %s"
    # #     # update_query = f"INSERT INTO `{InfoID}` (DelConfirmSignatureDict) VALUES (%s)"
    # #     cursor.execute(update_query, (DelConfirmSignatureDict,UserID))
    # #     print(f"[info] TransData from {UserID} has been inserted!")
    # #     cursor.close()
    # #     self.__conn.commit()
    #
    def insert_newrecord(self, AffairsID, DelConfirmSignatureDict,InfoID):
        cursor = self.__conn.cursor()
        try:
            if not self.__table_exists(self.__database):
                print_with_timestamp(f"本企业中的信息记录存储数据表不存在，正在被创建···")
                create_table_query = f"""
                CREATE TABLE `{self.__database}` (
                    AffairsID VARCHAR(255),
                    UserID VARCHAR(255),
                    InfoID VARCHAR(255),
                    DeleteMethod VARCHAR(255),
                    DeleteGranularity VARCHAR(255),
                    DeleteNotifyTree TEXT,
                    DelConfirmSignatureDict TEXT,
                    triggerType VARCHAR(255),
                    SourceDomain VARCHAR(255),
                    TimeLimit VARCHAR(255),
                    CountLimit INT
                )
                """
                cursor.execute(create_table_query)
                print_with_timestamp(f"本企业中的信息记录存储数据表创建成功！")

            # update_query = "UPDATE `{UserID}` SET DelConfirmSignatureDict = %s WHERE InfoID = %s"
            # cursor.execute(update_query, (UserID,DelConfirmSignatureDict, InfoID))
            update_query = "UPDATE {} SET DelConfirmSignatureDict = %s WHERE InfoID = %s AND AffairsID = %s".format(self.__database)
            cursor.execute(update_query, (DelConfirmSignatureDict, InfoID, AffairsID))

            # print(f"[info] TransData from {UserID} has been inserted!")

            self.__conn.commit()
        except Exception as e:
            print(f"Error: {e}")
            self.__conn.rollback()
        finally:
            cursor.close()


   #################### 此处开始查询信息，给删除效果评测推送
    def search_IntentLog(self, affairsID, infoID):
        cursor = self.__conn.cursor()
        try:
            if not self.__table_exists(self.__database):
                print_with_timestamp(f"[info] Table for {self.__database} not exist")
            search_query = "SELECT UserID, DeleteMethod, DeleteGranularity, SourceDomain, TimeLimit, CountLimit FROM {} WHERE InfoID = %s AND AffairsID = %s ".format(self.__database)
            cursor.execute(search_query, (infoID, affairsID))
            results = cursor.fetchall()
            self.__conn.commit()
            print_with_timestamp("数据查询成功！")
            return results
        except Exception as e:
            print(f"Error: {e}")
            self.__conn.rollback()
        finally:
            cursor.close()
    def search_ReqestLog(self, affairsID, infoID):
        cursor = self.__conn.cursor()
        try:
            if not self.__table_exists(self.__database):
                print_with_timestamp(f"[info] Table for {self.__database} not exist")
            search_query = "SELECT UserID, DeleteMethod, DeleteGranularity, SourceDomain, TimeLimit, CountLimit FROM {} WHERE InfoID = %s AND AffairsID = %s  ".format(self.__database)
            cursor.execute(search_query, (infoID, affairsID))
            results = cursor.fetchall()
            self.__conn.commit()
            print_with_timestamp("数据查询成功！")
            return results
        except Exception as e:
            print(f"Error: {e}")
            self.__conn.rollback()
        finally:
            cursor.close()

    def search_TriggerLog(self, affairsID, infoID):
        cursor = self.__conn.cursor()
        try:
            if not self.__table_exists(self.__database):
                print_with_timestamp(f"[info] Table for {self.__database} not exist")
            search_query = "SELECT UserID, DeleteMethod, DeleteGranularity, triggerType FROM {} WHERE InfoID = %s AND AffairsID = %s ".format(self.__database)
            cursor.execute(search_query, (infoID, affairsID))
            results = cursor.fetchall()
            self.__conn.commit()
            print_with_timestamp("数据查询成功！")
            return results
        except Exception as e:
            print(f"Error: {e}")
            self.__conn.rollback()
        finally:
            cursor.close()

    def search_notifyLog(self, affairsID, infoID):
        cursor = self.__conn.cursor()
        try:
            if not self.__table_exists(self.__database):
                print_with_timestamp(f"[info] Table for {self.__database} not exist")
            search_query = "SELECT UserID, DeleteMethod, DeleteGranularity, DeleteNotifyTree FROM {} WHERE InfoID = %s AND AffairsID = %s ".format(self.__database)
            cursor.execute(search_query, (infoID, affairsID))
            results = cursor.fetchall()
            self.__conn.commit()
            print_with_timestamp("数据查询成功！")
            return results
        except Exception as e:
            print(f"Error: {e}")
            self.__conn.rollback()
        finally:
            cursor.close()
    def search_confirmLog(self, affairsID, infoID):
        cursor = self.__conn.cursor()
        try:
            if not self.__table_exists(self.__database):
                print_with_timestamp(f"[info] Table for {self.__database} not exist")
            # search_query = "SELECT UserID, DeleteMethod, DeleteGranularity, DeleteNotifyTree, DelConfirmSignatureDict FROM {} WHERE InfoID = %s AND AffairsID = %s ".format(self.__database)
            search_query = "SELECT * FROM {} WHERE InfoID = %s AND AffairsID = %s".format(self.__database)
            cursor.execute(search_query, (infoID, affairsID))
            results = cursor.fetchall()
            self.__conn.commit()
            print_with_timestamp("数据查询成功！")
            return results
        except Exception as e:
            print(f"Error: {e}")
            self.__conn.rollback()
        finally:
            cursor.close()


    def searchinfoall(self, affairsID, infoID):
        cursor = self.__conn.cursor()
        try:
            if not self.__table_exists(self.__database):
                print_with_timestamp(f"[info] Table for {self.__database} not exist")
            search_query = "SELECT * FROM {} WHERE InfoID = %s AND AffairsID = %s ".format(self.__database)
            cursor.execute(search_query, (infoID, affairsID))
            results = cursor.fetchall()
            self.__conn.commit()
            print_with_timestamp("数据查询成功！")
            return results
        except Exception as e:
            print_with_timestamp(f"Error: {e}")
            self.__conn.rollback()
        finally:
            cursor.close()

    # def get_records_by_infoID(self, infoID):
    #     try:
    #         cursor = self.conn.cursor(dictionary=True)
    #         query = "SELECT * FROM OperationLog WHERE infoID = %s"
    #         cursor.execute(query, (infoID,))
    #         rows = cursor.fetchall()
    #         cursor.close()
    #
    #         # 将查询结果转换为 JSON 列表
    #         return json.dumps(rows, default=str)  # 使用 default=str 以处理日期时间对象
    #     except Error as e:
    #         print(f"An error occurred while querying the record: {e}")
    #         raise
    #
    # def get_records_by_infoID_affairsID(self, infoID, affairsID):
    #     try:
    #         cursor = self.conn.cursor(dictionary=True)
    #         query = "SELECT * FROM OperationLog WHERE infoID = %s and affairsID = %s"
    #         cursor.execute(query, (infoID, affairsID,))
    #         rows = cursor.fetchall()
    #         cursor.close()
    #
    #         # 将查询结果转换为 JSON 列表
    #         return json.dumps(rows, default=str)  # 使用 default=str 以处理日期时间对象
    #     except Error as e:
    #         print(f"An error occurred while querying the record: {e}")
    #         raise
    #
    # def get_records_by_time_period(self, start_time, end_time):
    #     try:
    #         cursor = self.conn.cursor(dictionary=True)
    #         query = "SELECT * FROM OperationLog WHERE submittime BETWEEN %s AND %s"
    #         cursor.execute(query, (start_time, end_time))
    #         rows = cursor.fetchall()
    #         cursor.close()
    #
    #         # 将查询结果转换为 JSON 列表
    #         return json.dumps(rows, default=str)  # 使用 default=str 以处理日期时间对象
    #     except Error as e:
    #         print(f"An error occurred while querying the record: {e}")
    #         raise




#
# if __name__ == "__main__":
#     processor = InfoMemory(
#         host="localhost",
#         user="root",
#         port=3306,
#         password="123456",
#         database="project26"
#     )
#     print(processor.table_exists("B00001"))
