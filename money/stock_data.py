# 创建API对象
import time

import pandas as pd
import pymysql
from pytdx.hq import TdxHq_API

api = TdxHq_API()
# 连接到行情服务器
api.connect('119.147.212.81', 7709)

conn = pymysql.connect(host='192.168.1.4', user='root', password='123456',
                      db='moto')


def get_online_all_price():

    dataframe = pd.read_excel('可转债.xlsx')
    codes = dataframe['转债代码']

    # 创建一个游标对象
    cursor = conn.cursor()
    insert_query = "INSERT INTO order_data (reversed_bytes0, code, price, cur_vol, reversed_bytes9, servertime) VALUES (" \
                   "%s, %s, %s, %s, %s, %s) "

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
            # my_dict_all.extend(my_dicts)
            for my_dict in my_dicts:
                # data_dict = dict(my_dict)
                data_dict = {'reversed_bytes0': my_dict['reversed_bytes0'], 'code': my_dict['code'], 'price': my_dict['price'],
                             'cur_vol': my_dict['cur_vol'], 'reversed_bytes9': my_dict['reversed_bytes9'], 'servertime': my_dict['servertime']}
                my_dict_all.append(data_dict)
        my_df = pd.DataFrame(my_dict_all)
        # 构造数据值的元组列表
        values = [tuple(row) for row in my_df.values]

        # 执行批量插入操作
        cursor.executemany(insert_query, values)
        conn.commit()
        print('插入数据')
        # my_df = my_df.sort_values('reversed_bytes9', ascending=False).head(3)
        time.sleep(3)


if __name__ == '__main__':
    get_online_all_price()