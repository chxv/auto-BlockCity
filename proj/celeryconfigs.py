from __future__ import absolute_import  # 拒绝隐式引入，因为celery.py的名字和celery的包名冲突，需要使用这条语句让程序正确地运行
from celery.schedules import crontab

# timezone = 'Asia/Shanghai'  # 时区
result_expires = 300  # Optional configuration, see the application user guide.

task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']

# 需要执行任务的配置
beat_schedule = {
    "test1": {
        "task": "proj.tasks.main",  # 执行的函数
        "schedule": crontab(minute=0, hour="*/2"),   # every 2 hour
        "args": ()  # 任务函数参数
    },
}








