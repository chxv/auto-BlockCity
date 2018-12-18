import security  # 一些被单独存放的个人信息

locations = [
    "{\"longitude\":118.79245862680000,\"latitude\":31.97214154340000}",  # 南京南站
    "{\"longitude\":118.79021066000000,\"latitude\":32.08932593810000}",  # 南京站
    "{\"longitude\":118.81472823390000,\"latitude\":32.04277108770000}",  # 南京玄武区大学城
    "{\"longitude\":121.49845300360000,\"latitude\":31.24005921830000}",  # 上海东方明珠
    "{\"longitude\":121.32554577910000,\"latitude\":31.19536438900000}",  # 上海虹桥站/虹桥国际机场
    "{\"longitude\":121.44646239920000,\"latitude\":31.02530439650000}",  # 上海交大/华东师范
    "{\"longitude\":120.21117593640000,\"latitude\":30.29401540160000}",  # 杭州东站
    "{\"longitude\":120.16063659580000,\"latitude\":30.25609282200000}",  # 杭州西湖
    "{\"longitude\":120.36644810610000,\"latitude\":30.32036270150000}",  # 杭州下沙大学城
    "{\"longitude\":113.25382653960000,\"latitude\":23.14917076990000}",  # 广州站
    "{\"longitude\":113.35489492130000,\"latitude\":23.14511450450000}",  # 广州番禹区大学城
    "{\"longitude\":114.11176707950000,\"latitude\":22.53665000020000}",  # 深圳站
    "{\"longitude\":114.02876634310000,\"latitude\":22.61184049670000}",  # 深圳北站
]

login_info = [
    security.mydevice  # 设备信息
]

configs = {
    'self_id': security.myuserid,  # 用户id
    'Authorization': security.myauthorization,  # 每次登录的token

    # post data
    'locations': locations,  # 一个位置字符串(json)列表
    'login_info': login_info[0],  # 日常登录的登录信息, 默认不修改
    
    # url
    'status_url': 'https://walletgateway.gxb.io/miner/{}/mine/list/v2',  # 自我果实成熟状态
    'gather_url': 'https://walletgateway.gxb.io/miner/{}/mine/{}/v2',  # 自我果实收获
    # change参数为true则更换其他用户列表，hasLocation为false则只显示剩下可收用户数
    'other_users_url': 'https://walletgateway.gxb.io/miner/steal/user/list/v2?change={}&hasLocation={}',
    # 其他用户的果实状况
    'other_status_url': 'https://walletgateway.gxb.io/miner/steal/{}/mine/list',
    # 收获其他人的果实
    'gather_other_url': 'https://walletgateway.gxb.io/miner/steal/{}/mine/{}',
    # 收取我的果实的人(每页显示50人,超过50会异常返回数据)
    'gather_me_users_url': 'https://walletgateway.gxb.io/miner/steal/record/list?pageNo={}&pageSize=50',
    # 修改自己的定位
    'set_location_url': 'https://walletgateway.gxb.io/customer/location/upload',
    # 日常登录
    'daily_login_url': 'https://walletgateway.gxb.io/customer/daily/signin/v2',

    # 每个用户的id有效时间
    'item_expire_time': 60*60*24*3
}





