# 获取历史数据存入ck
import uuid

import pandas as pd
from clickhouse_driver import Client
from mootdx.quotes import Quotes

ck_client = Client(host='192.168.1.4', port=9000)
tdx_client = Quotes.factory(market='std')


def get_online_all_price():

    dataframe = pd.read_excel('可转债.xlsx')
    codes = dataframe['代码']

    stock_list = []
    for code in codes.items():
        stock_list.append(str(code[1]))
    merged_df = None
    stock_list = ['128041']
    for stock in stock_list:
        print(f'{stock}')
        batch_sizes = [0, 2000, 4000]
        for batch_size in batch_sizes:
            df = tdx_client.transactions(symbol=stock, start=batch_size, offset=2000, date='20230815')
            df.insert(0, 'code', stock)
            df.insert(1, 'date', '2023-08-15')
            merged_df = pd.concat([df, merged_df], ignore_index=True)
    # 将索引转换为ID列
    merged_df = merged_df.reset_index()
    merged_df = merged_df.rename(columns={'index': 'index_value'})
    # merged_df['id'] = merged_df['id'].apply(lambda x: '2023081' + str(x))
    ck_client.execute('INSERT INTO moto.tick_data  (index_value, code, dt, time, price, vol, buyorsell, volume) VALUES',
                      [tuple(x) for x in merged_df.values])


if __name__ == '__main__':
    get_online_all_price()