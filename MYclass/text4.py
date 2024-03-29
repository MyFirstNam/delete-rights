import asyncio
from aiohttp import ClientSession
from flask import Flask, jsonify
import threading

app = Flask(__name__)


# async def send_post_request(session, url, data):
#     async with session.post(url, json=data) as response:
#         response_text = await response.text()
#         print(f"Response from {url}: {response_text}")  # 打印每个请求的响应



import asyncio
from aiohttp import ClientSession, ClientTimeout

async def send_post_request(session, url, data):
    try:
        # 使用 asyncio.wait_for 设置 5 秒超时
        response_text = await asyncio.wait_for(session.post(url, json=data), timeout=5.0)
        # 读取响应内容
        text = await response_text.text()
        print(f"Response from {url}: {text}")
    except asyncio.TimeoutError:
        # 如果发生超时，执行这里的代码
        print(f"Request to {url} timed out after 5 seconds")
    except Exception as e:
        # 处理其他可能的异常
        print(f"Request to {url} failed: {e}")
# 其他代码保持不变


async def send_requests_to_urls(urls, data):
    async with ClientSession() as session:
        # 创建一个任务列表，每个任务对应一个 URL
        tasks = [send_post_request(session, url, data) for url in urls]
        # 并发执行所有请求
        # await asyncio.gather(*tasks)
        await asyncio.gather(*tasks, return_exceptions=True)

def background_asyncio_task(loop, coro):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(coro)


@app.route('/process', methods=['POST'])
def send_posts():

    print("接收到请求！")
    data = {'key': 'value'}
    urls = [
        f"http://127.0.0.1:10000/do_something",
        f"http://127.0.0.1:10000/do_something1",
        f"http://127.0.0.1:10000/do_something2"
    ]
    loop = asyncio.new_event_loop()
    task = send_requests_to_urls(urls, data)
    threading.Thread(target=background_asyncio_task, args=(loop, task)).start()
    print("主进程执行成功")

    return jsonify({"message": "POST requests are being sent asynchronously to multiple URLs"})





if __name__ == "__main__":
    app.run(host='127.0.0.1', port=10001, debug=True)
