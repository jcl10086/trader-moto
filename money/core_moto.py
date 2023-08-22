# 买入策略
import time

import pandas as pd

from money.core import tdx_client


def get_codes():
    dataframe = pd.read_excel('股票.xlsx')
    codes = dataframe['代码']

    stock_list = []
    for code in codes.items():
        stock_list.append(str(code[1]))
    return stock_list


def get_speed(stock_list):
    stock_list = stock_list[0:2200]
    my_df = None
    batch_size = 50
    for i in range(0, len(stock_list), batch_size):
        df = tdx_client.quotes(symbol=stock_list[i:i + batch_size])
        my_df = pd.concat([my_df, df], ignore_index=True)
    # 过滤未上市
    my_df = my_df[my_df['price'] > 0]
    # 过滤条件：reversed_bytes0
    my_df = my_df[(my_df['reversed_bytes9'] >= 0.8) & (my_df['reversed_bytes9'] <= 3)]
    # 按照Score列进行降序排序，并获取Top 3行
    my_df = my_df.nlargest(3, 'reversed_bytes9')
    return my_df


def buy_strategy1(code):
    flag = False
    df = tdx_client.transaction(symbol=code, start=0, offset=40)
    num_buy = df[df['buyorsell'] == 0]['vol'].sum()
    num_all = df['vol'].sum()
    diff = num_buy / num_all
    if diff > 0.9:
        flag = True
    print(f'{code}  {flag}')


def job_core():
    stock_list = get_codes()
    while True:
        my_df = get_speed(stock_list)
        for index, row in my_df.iterrows():
            buy_strategy1(row['code'])
        time.sleep(3)


if __name__ == '__main__':
    job_core()