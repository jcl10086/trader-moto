import time
from datetime import datetime

import pandas as pd
from mootdx.quotes import Quotes
import pymysql
import pywencai

conn = pymysql.connect(host='192.168.1.4', user='root', password='123456')

tdx_client = Quotes.factory(market='std')


def get_price(codes):
    code_df = None
    batch_size = 50
    for i in range(0, len(codes), batch_size):
        df = tdx_client.quotes(symbol=codes[i:i + batch_size])
        code_df = pd.concat([code_df, df], ignore_index=True)
    return code_df


def save_data(zz_array):
    sql = 'insert into data.online_data(name,code,dt,price,cur_vol) values(%s,%s,%s,%s,%s)'
    values = [(item["name"], item["code"], item["dt"], item["price"], item["cur_vol"]) for item in zz_array]
    cursor.executemany(sql, values)
    conn.commit()


def job(codes):
    zz_array = []
    code_df = get_price(codes)
    for index, row in code_df.iterrows():
        code = row['code']
        price = row['price']
        cur_vol = row['cur_vol']
        zz_json = {
            'code': code,
            'dt': formatted_time,
            'name': '',
            'price': price,
            'cur_vol': cur_vol
        }
        zz_array.append(zz_json)
    save_data(zz_array)


if __name__ == '__main__':
    cursor = conn.cursor()
    codes = []
    df = pywencai.get(query='可转债，价格>60', loop=True, sort_order='asc', query_type='conbond')
    code_array = df['可转债@可转债代码']
    for ca in code_array:
        codes.append(ca.split('.')[0])
    while True:
        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        if current_time.hour >= 15 or current_time.hour <= 9:  # 15 表示下午3点
            break
        job(codes)
        print(f'{formatted_time}')
        time.sleep(3)