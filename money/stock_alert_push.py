import time

import pandas as pd

from mootdx.quotes import Quotes

from money import data_util

client = Quotes.factory(market='std')
dataframe = pd.read_excel('可转债.xlsx')

codes_before = []
codes_after = []


# 获取股票
def get_stocks():
    codes = dataframe['代码']
    stock_list = []
    for code in codes.items():
        stock_list.append(str(code[1]))
    return stock_list


# 获取实时数据
def get_online_datas(stock_list):
    merged_df = None
    batch_size = 80
    for i in range(0, len(stock_list), batch_size):
        df = client.quotes(symbol=stock_list[i:i + batch_size])
        merged_df = pd.concat([merged_df, df], ignore_index=True)
    return merged_df


def alert_strategy1(merged_df):
    # 最大价格与当前价格差值
    merged_df['diff'] = (merged_df['high'] - merged_df['price']) / merged_df['price']
    merged_df = merged_df[round(merged_df['diff'] * 100, 2) > 5]
    # 今日涨幅
    merged_df['zf'] = (merged_df['price'] - merged_df['last_close']) / merged_df['last_close']
    # 今日最大涨幅
    merged_df['max_zf'] = (merged_df['high'] - merged_df['last_close']) / merged_df['last_close']
    # merged_df = merged_df[merged_df['reversed_bytes9'] > 0.3]
    merged_df = merged_df.sort_values(by='diff', ascending=False).reset_index()
    contents = []
    for row in merged_df.itertuples():
        diff = round(row.diff * 100, 2)
        zf = round(row.zf * 100, 2)
        max_zf = round(row.max_zf * 100, 2)
        name = dataframe[dataframe['代码'] == int(row.code)].values[0][1]
        content = f'{name}  {row.code}：差值空间{diff}%  今日最大涨幅：{max_zf}   今日涨幅：{zf}%'
        # contents.append(content)
        contents.append(row.code)
        codes_after.append(row.code)
        # data_util.wx_push(content)
        # print(f'{name}  {row.code}：差值空间{diff}%  最大涨幅：{max_zf}   今日涨幅：{zf}%')
    # if codes_before != codes_after:
    #     data_util.wx_push(contents)
    # codes_after = codes_before
    return contents


if __name__ == '__main__':
    stock_list = get_stocks()
    while True:
        merged_df = get_online_datas(stock_list)
        contents = alert_strategy1(merged_df)
        # contents = contents[0:1]
        if codes_before != codes_after:
            data_util.wx_push(str(contents))
        codes_before = codes_after
        time.sleep(3)