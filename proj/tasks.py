from __future__ import absolute_import, unicode_literals
from .celery import app
from configs import configs, locations
from dataManager import DataManager
import time
from datetime import datetime
import requests
import json
# import redis

dm = DataManager()


def get_utc_time(date_t: datetime):
    """获取指定的北京时间的utc时间"""
    t = date_t.timestamp()  # 目标时间的unix时间戳
    return datetime.utcfromtimestamp(t)


def send(url, method='get', data=None) -> dict:
    if method == 'get' or method == 'GET':
        headers = {'Authorization': configs['Authorization']}
        r = requests.get(url, headers=headers)  # request

    elif method == 'post' or method == 'POST':
        headers = {
            'Authorization': configs['Authorization'],
            'Content-Type': 'application/json;charset=UTF-8'
        }
        if data:
            r = requests.post(url, data=data, headers=headers)
        else:
            r = requests.post(url, headers=headers)

    else:
        return {'Error': '[BlockCity] error http method in function send'}

    # 处理请求返回内容
    if r.status_code == 200:
        text = r.content.decode('utf8')
        return json.loads(text)
    else:
        return {'Error': '[BlockCity] error token or operation'}


@app.task
def how_about_me():
    """查看自己的果实成熟状况

    指定部分收获任务给gather"""
    url = configs['status_url'].format(configs['self_id'])
    response = send(url)
    if 'Error' in response:  # 检查有没有返回404之类的错误
        return response['Error']

    # 解析响应
    # 确保剩余成熟果实大于1的前提下,收获掉所有成熟果实
    # 返回数据包里的果实位置已经按成熟时间从过去到现在排序了,反向遍历保留第一个果实即可
    mines = response['data']['mines']
    have_matured = False  # 存在成熟果实
    now = time.time()  # 此时
    for mine in reversed(mines):
        if mine['validTime']//1000 < now:  # 成熟
            if have_matured:  # 已经保留了成熟果实(直接收获)
                gather.delay(mine['id'])
            else:
                have_matured = True  # 当前果实为成熟果实,pass
        else:
            pass  # 不成熟的不处理


@app.task
def gather(target=None) -> bool:
    """收获自己果实"""
    # target 可留白
    if target:
        # 若指明收获的果实id
        url = configs['gather_url'].format(configs['self_id'], target)
        r = send(url)

        return True
    else:
        print('[-] Nothing was gathered')
        return False


@app.task
def user_list(change='false', hasLocation='true'):
    """查看可以操作的其他用户

    保存所有用户id"""
    url = configs['other_users_url'].format(change, hasLocation)
    response = send(url)
    if 'Error' in response:  # 检查有没有返回404之类的错误
        return response['Error']

    leftAmount = response['data']['leftAmount']
    counts = 72  # 为免异常,限制每次最多读取72个附近的人
    users = set()
    for user in response['data']['list']:
        users.add(user['userId'])

    while leftAmount > 0 or counts > 0:
        try:
            url = configs['other_users_url'].format('true', hasLocation)
            response = send(url)
            counts -= 8
            leftAmount = response['data']['leftAmount']
            for user in response['data']['list']:
                users.add(user['userId'])

        except Exception as e:
            print(repr(e))
    # 保存用户id
    for i in users:
        dm.store(i)


@app.task
def how_about_other(target_user: str):
    """查看指定id的用户的果实成熟状态

    收获所有成熟果实且将不成熟的果实加入任务队列"""
    url = configs['other_status_url'].format(target_user)
    response = send(url)
    if 'Error' in response:  # 检查有没有返回404之类的错误
        return response['Error']
    # 解析数据
    now = time.time()
    for i in response['data']:
        if i['validDate']//1000 > now:  # 时间未到
            delay_time = i['validDate']//1000 - now + 1
            gather_other.apply_async(args=(target_user, str(i['mineId'])), countdown=delay_time)
        else:  # 已成熟
            if i['canSteal']:  # 可以收取
                gather_other.delay(target_user, str(i['mineId']))


@app.task
def gather_other(target_user: str, target_coin: str):
    """偷取指定用户的指定果实"""
    url = configs['gather_other_url'].format(target_user, target_coin)
    return send(url)


@app.task
def gather_me_users(pageNo=1):
    """收获了我的果实的人

    保存用户id"""
    url = configs['gather_me_users_url'].format(pageNo)
    response = send(url)  # pageNo==1, 最近50个收获我果实的人
    if 'Error' in response:  # 检查有没有返回404之类的错误
        return response['Error']
    users = set()
    for user in response['data']:  # 解析response得到用户id
        users.add(user['stealUserId'])
    # 保存到数据库
    dm.multi_store(users)


@app.task
def set_location(location: str):
    """设置定位为 {location} """
    url = configs['set_location_url']
    data = location
    return send(url, method='post', data=data)


@app.task
def daily_login():
    """日常登录领取算力"""
    url = configs['daily_login_url']
    data = configs['login_info']  # 直接使用默认登录信息
    return send(url, method='post', data=data)


@app.task
def main():
    """BlockCity 的主函数,周期性执行

    [0] 检查网络连接,若无网络则跳过,等待下次执行

    [1] 日常登录
    [2] 检查自己的果实状态,收获到只剩一个果实
    [3] 更新位置信息

    [4] 将附近可以直接偷取的人,及偷取我的果实的人的id加入名单

    [5] 读取数据库获得已存储的用户名单
    [6] 将名单上的所有人加入扫描任务列表
    [7] 在扫描每一个用户的同时,将其被收获的果实加入收获,或待收获任务列表
    """
    # 先检查网络
    retry_times = 3  # 重试次数
    while retry_times:
        try:
            retry_times -= 1
            r = requests.get('https://ident.me')  # 尝试发包
            break  # 若执行到这里则发包无异常, 就继续下一环节
        except Exception as e:
            if retry_times == 0:
                return '[BlockCity] check ip error: ' + repr(e)  # 网络错误,下一次再试
            time.sleep(1)

    daily_login.delay()  # 日常登录
    how_about_me.delay()  # 检查自己
    # 更新位置
    day = int(time.time()) // (24*60*60)  # 秒时间戳转化为日时间戳
    loc = locations[day % len(locations)]  # 位置每天一换
    set_location.delay(loc)

    # 查询然后保存用户id
    user_list.delay()  # 遍历用户列表
    gather_me_users.delay(1)  # 偷取我的果实的人0-49
    gather_me_users.delay(2)  # ............ 50-99

    # 对所有用户逐一排查
    # 读取数据库
    users = dm.readout()
    for i in users:
        how_about_other.delay(i)
        time.sleep(0.1)  # 让任务与任务之间留一点缓冲,虽然我也不知道有没有用

    return True


@app.task
def test():
    return "test"







