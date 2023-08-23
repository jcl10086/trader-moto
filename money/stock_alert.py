# 获取当日最高价差值
import time

import pandas as pd
from mootdx.quotes import Quotes

from money import data_util
from money.data_util import wx_push


def job():
    client = Quotes.factory(market='std')

    dataframe = pd.read_excel('可转债.xlsx')
    codes = dataframe['代码']

    stock_list = []
    for code in codes.items():
        stock_list.append(str(code[1]))

    merged_df = None
    batch_size = 80
    for i in range(0, len(stock_list), batch_size):
        df = client.quotes(symbol=stock_list[i:i + batch_size])
        merged_df = pd.concat([merged_df, df], ignore_index=True)

    # 删选出当日最大涨幅大于3%
    merged_df = merged_df[(merged_df['high'] - merged_df['last_close']) / merged_df['last_close'] > 0.028].reset_index()
    # 最大价格与当前价格差值
    merged_df['diff'] = (merged_df['high'] - merged_df['price']) / merged_df['price']
    # 今日涨幅
    merged_df['zf'] = (merged_df['price'] - merged_df['last_close']) / merged_df['last_close']
    # 今日涨幅
    merged_df['max_zf'] = (merged_df['high'] - merged_df['last_close']) / merged_df['last_close']
    merged_df = merged_df.sort_values(by='diff', ascending=False).reset_index()

    for row in merged_df.itertuples():
        diff = round(row.diff * 100, 2)
        if diff < 5:
            continue
        zf = round(row.zf * 100, 2)
        max_zf = round(row.max_zf * 100, 2)
        name = dataframe[dataframe['代码'] == int(row.code)].values[0][1]
        content = f'{name}  {row.code}：差值空间{diff}%  最大涨幅：{max_zf}   今日涨幅：{zf}%'
        data_util.wx_push(content)
        # print(f'{name}  {row.code}：差值空间{diff}%  最大涨幅：{max_zf}   今日涨幅：{zf}%')


if __name__ == '__main__':
    while True:
        job()
        time.sleep(60)