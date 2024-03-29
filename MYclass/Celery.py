# tasks.py
import time

from celery import Celery

app = Celery('tasks', broker='pyamqp://guest@localhost//')

@app.task
def perform_task(data):
    # 在这里执行你的后续操作，可以是耗时的任务
    print(f"Performing task with data: {data}")
    time.sleep(10)
