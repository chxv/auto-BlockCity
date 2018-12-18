import redis
import time
from configs import configs


"""
redis object:
    BlockCity-Users: 存储其他用户id的集合
"""
BlockCity_Users = 'BlockCity_Users'
item_expire_time = configs['item_expire_time']


class DataManager:
    """用来管理存储的用户id的数据"""
    def __init__(self, bcu=BlockCity_Users, iet=item_expire_time):
        self.BlockCity_Users = bcu
        self.item_expire_time = iet
        self.pool = redis.ConnectionPool(host='127.0.0.1', port=6379, decode_responses=True)

    def store(self, user_id: str) -> None:
        """存入一个用户id,若用户已存在则更新其有效时间"""
        red = redis.Redis(connection_pool=self.pool)
        red.sadd(self.BlockCity_Users, user_id)

    def multi_store(self, users_id: set) -> None:
        red = redis.Redis(connection_pool=self.pool)
        for i in users_id:
            red.sadd(self.BlockCity_Users, i)

    def readout(self) -> set:
        """返回包含所有id的一个集合"""
        red = redis.Redis(connection_pool=self.pool)
        return red.smembers(self.BlockCity_Users)











