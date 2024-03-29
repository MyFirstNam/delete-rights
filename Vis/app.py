# 文件名：app.py
from flask import Flask, render_template, send_from_directory, request, jsonify
from flask_socketio import SocketIO
import json
import time

from switcher import parse_tree

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
first = True

# 一个简单的网络图数据示例
# 更复杂的网络图数据
# graph_data = {
#     "nodes": [
#         {"id": "A", "group": 1, "value": 1},
#         {"id": "B", "group": 1, "value": 2},
#         {"id": "C", "group": 1, "value": 1},
#         {"id": "D", "group": 2, "value": 2},
#         {"id": "E", "group": 2, "value": 1},
#         {"id": "F", "group": 2, "value": 3},
#         {"id": "G", "group": 3, "value": 2},
#         {"id": "H", "group": 3, "value": 3},
#         {"id": "I", "group": 3, "value": 3}
#     ],
#     "links": [
#         {"source": "A", "target": "B", "value": 1},
#         {"source": "B", "target": "C", "value": 1},
#         {"source": "A", "target": "C", "value": 1},
#         {"source": "D", "target": "E", "value": 2},
#         {"source": "E", "target": "F", "value": 2},
#         {"source": "D", "target": "F", "value": 2},
#         {"source": "G", "target": "H", "value": 3},
#         {"source": "H", "target": "I", "value": 3},
#         {"source": "G", "target": "I", "value": 3},
#         {"source": "A", "target": "D", "value": 4},
#         {"source": "B", "target": "E", "value": 4},
#         {"source": "C", "target": "F", "value": 4},
#         {"source": "D", "target": "G", "value": 5},
#         {"source": "E", "target": "H", "value": 5},
#         {"source": "F", "target": "I", "value": 5}
#     ]
# }

graph_data = {"nodes": [{"id": "b1000"}, {"id": "b1001"},
                        {"id": "b1002"}, {"id": "b1003"},
                        {"id": "b1004"}],
              "links":
                  [{"source": "b1000", "target": "b1001", "id": "edge_1"},
                   {"source": "b1001", "target": "b1002", "id": "edge_2"},
                   {"source": "b1000", "target": "b1003", "id": "edge_3"},
                   {"source": "b1003", "target": "b1004", "id": "edge_4"}]}


@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


@app.route('/submit')
def submit():
    return send_from_directory('static', 'adaptive_submit.html')


@socketio.on('connect')
def on_connect():
    print("前后端连接成功...")
    # socketio.emit('graph_data', json.dumps(graph_data))


def update_edge_status(edge_id):
    # 在这里根据具体的逻辑处理边状态更新，示例中直接将边标识符发送给前端
    socketio.emit('edge_status_update', edge_id)


@app.route('/update_graph', methods=['POST'])
def update_graph():
    # TODO 联调
    # 接收 JSON 数据
    data = request.get_json()
    if data:
        nodes, links = parse_tree(None, json.loads(data))
        # 转换为 JSON
        graph_data_1 = json.dumps({"nodes": nodes, "links": links})
        print(graph_data_1)
        # 向客户端广播新的网络图数据
        socketio.emit('graph_data', graph_data_1)
        return jsonify({"message": "Graph data updated successfully."})
    return jsonify({"message": "No data provided."})


@app.route('/update_notify', methods=['POST'])
def update_notify():
    global first
    # 接收 JSON 数据
    data = request.get_json()
    if data:
        data = json.loads(data)
        socketio.emit('edge_status_update', (data["node_id"], first))
        first = False
        return jsonify({"message": "Graph data updated successfully."})
    return jsonify({"message": "No data provided."})


if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True,
                 host='127.0.0.1', port=20098)
