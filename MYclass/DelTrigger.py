import datetime
import time

def print_with_timestamp(message):
    current_time = datetime.datetime.now()
    timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")
class DelTrigger:
    """
    在接受用户请求的路由中，创建此类，用于解析和触发
    1.时间约束，这个东西应该是一个时刻，表示用户想要在某一个时刻进行删除，需要设置一个计时器！！！
    2.次数限制
    3.函数返回一个dict字典，用于表示 删除请求
    """
    def deleteTrigger(self, delintention:dict):
        """
        解析用户普通删除意图生成删除请求
        :param delintention:
        :return: delrequest
        """
        delrequest = {
            "affairs_id": delintention["affairs_id"],
            "user_id": delintention["user_id"],
            "info_id": delintention["info_id"],
            "deleteMethod": delintention["deleteMethod"],
            "deleteGranularity": delintention["deleteGranularity"]
        }
        print_with_timestamp("按需触发成功！")
        return delrequest

    def timeTrigger(self,delintention:dict):
        """
        解析用户带有时间设置的删除意图生成删除请求
        :param delintention:
        :return: delrequest
        """
        # 设置未来的时间点，例如在未来的n秒后继续执行
        future_time = datetime.datetime.now() + datetime.timedelta(seconds=delintention["time_limit"])
        while datetime.datetime.now() < future_time:
            # 检查当前时间是否已经达到了未来的时间点
            time.sleep(1)  # 每秒检查一次
        delrequest = {
            "affairs_id": delintention["affairs_id"],
            "user_id": delintention["user_id"],
            "info_id": delintention["info_id"],
            "time_limit": delintention["time_limit"],
            "deleteMethod": delintention["deleteMethod"],
            "deleteGranularity": delintention["deleteGranularity"]
        }
        print_with_timestamp("延时计时触发成功！")
        return delrequest

    def countTrigger(self,delintention:dict):
        """
        在满足条件后，调用deleteTrigger函数,
        通知数据库!!!!关于这个数据库，是不是应该由我们创建，但是这个数据库我们不应该创建
        在满足条件后，调用deleteTrigger函数，这个函数理解成一个计数器
        :param user_id:
        :param affairs_id:
        :param info_id:
        :param count_limit:
        :return:
        """
        delrequest = {
            "affairs_id": delintention["affairs_id"],
            "user_id": delintention["user_id"],
            "info_id": delintention["info_id"],
            "deleteMethod": delintention["deleteMethod"],
            "deleteGranularity": delintention["deleteGranularity"]
        }
        print_with_timestamp("计次触发成功！")
        return delrequest
