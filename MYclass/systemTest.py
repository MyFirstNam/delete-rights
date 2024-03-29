# import json
# import unittest
# from unittest.mock import patch
# from SendInfo import sendInfo

# loginfo = {
#     "userID": "b00001",
#     "infoID": "0x0001",
#     # "getLogType": "getDeleteIntentLog"  # 删除意图
#     # "getLogType":"getDeleteRequestLog"    #删除请求
#     # "getLogType":"getDeleteTriggerLog"    #删除触发
#     # "getLogType":"getDeleteNotificationLog"   #删除通知
#     "getLogType":"getDeleteConfirmationLog"   #删除确认
# }
# class TestSendInfo(unittest.TestCase):
#     @patch('requests.post')  # 使用unittest的patch装饰器模拟requests.post方法
#     def test_send_intent_log(self, mock_post):
#         mock_post.return_value.status_code = 200
#         # 模拟请求的JSON数据
#         loginfo = {
#             "getLogType": "getDeleteConfirmationLog",
#             "userID": "b00001",
#             "infoID": "0x0001"
#         }
#         loginfo = json.dumps(loginfo)
#         with sendInfo.test_client() as client:
#             response = client.post('/result/postx/endpointx', json=loginfo)
#
#         self.assertEqual(response.status_code, 200)
#        # self.assertTrue("POST请求成功" in response.data.decode())
#
# if __name__ == "__main__":
#     unittest.main()

import json
import unittest
from route_bus1 import userroute

# 模拟通知的 JSON 数据
with open('data.json', 'r') as json_file:
    sample_notification = json.load(json_file)
# 模拟确认的 JSON 数据
sample_confirmation = {
    "DataTransferPath_path": {
        # 添加确认数据结构
    },
    "affairs_id": "0001",
    "from_bus_id": "b1001",
    "to_bus_id": "b1002",
    "user_id": "b00001",
    "info_id": "0x0001",
    "DelConfirmSignatureDict": {
        "b1002": "signature_hash_here"
    }
}

class TestYourApp(unittest.TestCase):

    def setUp(self):
        self.userroute = userroute .test_client()

    def test_notifyAcc(self):
        # 测试通知路由
        response = self.userroute .post('/test/postx/endpointx', json=json.dumps(sample_notification))
        self.assertEqual(response.status_code, 200)
        self.assertIn(f"接收成功！", response.data)

    def test_delConfirmAcc(self):
        # 测试确认路由
        response = self.userroute .post('/confirm/postx/endpointx', json=json.dumps(sample_confirmation))
        self.assertEqual(response.status_code, 200)
        self.assertIn(f"POST请求成功", response.data)

        # 添加更多断言来测试其他方面的行为
        # 例如，验证签名、确认数不等于子节点数等情况

# 添加更多测试用例来覆盖不同的情况

if __name__ == '__main__':
    unittest.main()



