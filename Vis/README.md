# 前端展示实现
通过websocket实现后端实时将数据推送给前端
后端依赖
```shell
pip install flask-socketio flask-cors gmssl
```
前端依赖
d3.v6.min.js
socket.io.min.js

后端运行端口号
host 127.0.0.1
port 20098

## 网络初始化渲染
### 前端
D3.js渲染生成网络拓扑
所有节点和边到d3下进行查找
网络拓扑初始化函数：
```javascript
socket.on('graph_data', function(data) {
    const graph = JSON.parse(data);
    renderGraph(graph);  // 渲染图
});
```
### 后端
websocket连接时传输图数据
```python
socketio.emit('graph_data', json.dumps(graph_data))
```
后端联调端口：update_graph
## 网络通知状态变更
### 前端
```javascript
socket.on('edge_status_update', function(edgeId) {
    // 选择特定的元素
    var selectedElement = d3.select(`#${edgeId}`);
    // 使用 .empty() 方法检查是否找到了元素
    if (!selectedElement.empty()) {
        // 找到了元素
        console.log("已找到该元素");
        // 可以在这里执行您的操作，例如更改样式
        selectedElement.classed('red-link', true);
    } else {
        // 未找到元素
        console.log("未找到该元素");
    }
});
```
### 后端
```python
def update_edge_status(edge_id):
    # 在这里根据具体的逻辑处理边状态更新，示例中直接将边标识符发送给前端
    socketio.emit('edge_status_update', edge_id)
```
后端联调端口：update_notify

## To Deng Xin
### 首次启动
第一步 管理员运行cmd 首先启动数据库  net start mysql 

第二步，启动business,business1,business2,business3,business4

第三步，启动Central_authority,模拟中心监管机构，接收流转路径请求

第四步，启动vis/app.py,启动前端的后台，并打开该服务下的网页

第五步，启动User.py，打开adaptive_submit.html，填写内容提交表单

第六步，观察app.py对应index.html中的节点变化

### 重复调试
adaptive_submit.html中填写数据，提交内容

注意：
+ 两次重复调试，不要间隔时间太短，因为事件是有延迟的
+ 如果遇到动态展示链不更新显示的情况，可以刷新下网页，如果还不奏效，可以重新启动下app.py

### 可扩展
user.py中对提交的表单进行合法校验，错误返回前端响应进行提示

### 重构思路
1. 所有Business都是对象的实例，运行节点只是生成一个新实例，而不是不同py文件
2. 所有配置内容都抽取出来，放到yaml文件里面，通过python已有的库去解析yaml文件，尤其是host参数
3. 准备两个yaml文件，一个是自己单机调试的host，另一个是联调局域网host
4. 项目部署启动编写一个Linux shell脚本

### 给你安装的软件和环境
soft：

everything：搜索本机所有文件

utools：Alt+Space统一软件入口

Snipaste: F1截图工具

env（都已经添加环境变量）：

Anaconda：创建python虚拟环境

MiKTeX：LaTeX编译环境

