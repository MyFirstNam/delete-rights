import socket
# 建立一个服务端
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#参数可以不加
server.bind(('localhost', 50010))   # 绑定要监听的端口
server.listen(5)  # 开始监听 表示可以使用五个链接排队
# conn就是客户端链接过来而在服务端为期生成的一个链接实例
while True:
    while True:
        print('监听中')
        conn, addr = server.accept()  # 等待链接,多个链接的时候就会出现问题,其实返回了两个值
        try:
            payload_data1 = conn.recv(1024)[18:][:-16].decode()
            print(payload_data1)

            conn.send('YES'.encode('utf-8'))
            payload_data2 = conn.recv(1024)[18:][:-16].decode()  # 接收数据
            print(payload_data2)
            # 然后再发送数据
            msg = b"YES"
            conn.send(msg)
        except ConnectionResetError as e:
            print(addr, '关闭了与主机的链接！')
            break
        conn.close()