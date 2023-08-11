# 创建API对象
import time

import pandas as pd
import redis
from pytdx.hq import TdxHq_API

api = TdxHq_API()
# 连接到行情服务器
api.connect('119.147.212.81', 7709)

# 连接到Redis
r = redis.Redis(host='192.168.1.4', port=6379, db=0)
# 创建管道对象
pipe = r.pipeline()


def get_online_all_price():

    dataframe = pd.read_excel('可转债.xlsx')
    codes = dataframe['转债代码']

    while True:
        stock_list = []
        for code in codes.items():
            # xx.SZ  xx.SH
            if code[1].split('.')[1] == 'SZ':
                stock_list.append((0, str(code[1].split('.')[0])))
            elif code[1].split('.')[1] == 'SH':
                stock_list.append((1, str(code[1].split('.')[0])))
            else:
                continue
        # stock_list = [(0, '123205')]
        my_dict_all = []
        batch_size = 80
        for i in range(0, len(stock_list), batch_size):
            my_dicts = api.get_security_quotes(stock_list[i:i + batch_size])
            for my_dict in my_dicts:
                data_dict = {'reversed_bytes0': my_dict['reversed_bytes0'], 'code': my_dict['code'], 'price': my_dict['price'],
                             'cur_vol': my_dict['cur_vol'], 'reversed_bytes9': my_dict['reversed_bytes9']}
                my_dict_all.append(data_dict)
        for item in my_dict_all:
            pipe.hmset(f'order:{item["code"]}:{item["reversed_bytes0"]}', {key: value for key, value in item.items()})
            # 设置键的过期时间为 60 秒
            r.expire(f'order:{item["code"]}:{item["reversed_bytes0"]}', 120)
        pipe.execute()
        print('插入数据')
        time.sleep(3)


if __name__ == '__main__':
    get_online_all_price()