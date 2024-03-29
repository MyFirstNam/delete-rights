# 文件名：app.py

from flask import Flask, render_template
from flask_socketio import SocketIO
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# 一个简单的网络图数据示例
graph_data = {
    "nodes": [{"id": "A"}, {"id": "B"}, {"id": "C"}],
    "links": [{"source": "A", "target": "B"}, {"source": "A", "target": "C"}]
}


@app.route('/')
def index():
    return render_template('static/index.html')


@socketio.on('connect')
def on_connect():
    # 当客户端连接时发送图数据
    socketio.emit('graph_data', json.dumps(graph_data))


if __name__ == '__main__':
    socketio.run(app, debug=True)
