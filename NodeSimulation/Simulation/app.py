"""
此py文件是整个程序的启动入口
负责启动当前节点（企业）中的所有监听路由
具体包括：
1.启动删除指令通知与确认系统接收删除效果评测系统的路由端口
2.启动删除指令通知与确认系统接收用户/上级节点的路由端口，接收到的内容为：删除意图/删除通知
3.启动删除指令通知与确认系统接下级节点的路由端口，接收到的内容为：删除通知确认
"""
import argparse
from flask import Flask

from ..Model.EnterpriseNode import EnterpriseNode
from blueprints.user_business import enterprise_blue

app = Flask(__name__)

# 设置全局变量
node = EnterpriseNode()

# 绑定蓝图
app.register_blueprint(enterprise_blue)


if __name__ == "__main__":
    # 创建一个解析器
    parser = argparse.ArgumentParser()

    # 添加命令行参数
    parser.add_argument("bus_id", type=str, help="first arg")
    parser.add_argument("port", type=int, help="second arg")
    parser.add_argument("ip",type=str, help="second arg",)

    # 解析命令行参数
    args = parser.parse_args()

    # 配置端口
    port = args.port


    # 访问参数
    # print("bus_id:", args.bus_id)
    # print("port:", port)

    host = '0.0.0.0'

    app.run(host, port)