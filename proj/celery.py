from __future__ import absolute_import, unicode_literals
from celery import Celery
# from celery.schedules import crontab

app = Celery('proj',
             broker='redis://localhost:6379',
             backend='redis://localhost:6379',
             include=['proj.tasks'])

app.config_from_object('proj.celeryconfigs')


# @app.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):
#     sender.add_periodic_task(10.0, test.s('hello'), name='add every 10')
#
#     sender.add_periodic_task(
#         crontab(hour=21, minute=38, day_of_week=6),
#         test.s('Happy Mondays!'),
#     )
#
#
# @app.task
# def test(arg):
#     print(arg)


if __name__ == '__main__':
    app.start()

