# 买入策略
import math
import time

import pandas as pd

from mootdx.quotes import Quotes

tdx_client = Quotes.factory(market='std')


def get_codes():
    dataframe = pd.read_excel('可转债.xlsx')
    codes = dataframe['代码']

    stock_list = []
    for code in codes.items():
        stock_list.append(str(code[1]))
    return stock_list


# 获取涨速
def get_speed(stock_list):
    # stock_list = stock_list[0:2200]
    my_df = None
    batch_size = 50
    for i in range(0, len(stock_list), batch_size):
        df = tdx_client.quotes(symbol=stock_list[i:i + batch_size])
        my_df = pd.concat([my_df, df], ignore_index=True)
    # 过滤未上市
    my_df = my_df[my_df['price'] > 0]
    # 过滤条件：reversed_bytes9
    my_df = my_df[(my_df['reversed_bytes9'] >= 0.5) & (my_df['reversed_bytes9'] <= 3)]
    # 过滤涨幅
    my_df = my_df[(my_df['price'] - my_df['last_close']) / my_df['last_close'] * 100 < 12]
    # 按照Score列进行降序排序，并获取Top 3行
    my_df = my_df.nlargest(5, 'reversed_bytes9')
    return my_df


# 买入策略1
def buy_strategy1(code):
    flag = False
    df = tdx_client.transaction(symbol=code, start=0, offset=20)
    num_buy = df[df['buyorsell'] == 0]['vol'].sum()
    num_all = df['vol'].sum()
    num_avg = df['vol'].mean()
    diff = num_buy / num_all
    if diff > 0.7 and num_avg > 500:
        flag = True
    print(f'{code}  {flag}')
    return flag


# 挂单买入
def buy_info(code, current_price, current_balance):
    # 挂单股价
    gd_price = current_price * 1.03
    gd_price = round(gd_price, 2)
    # 挂单数量
    gd_num = math.floor(current_balance / gd_price / 10) * 10
    print(f'挂单价格：{gd_price}  挂单数量：{gd_num}')
    # 买入
    tdx_client.buy(code, price=gd_price, amount=gd_num)
    return gd_num


# 卖出策略1
def sell_strategy1(code):
    flag = False
    df = tdx_client.transaction(symbol=code, start=0, offset=20)
    num_buy = df[df['buyorsell'] == 1]['vol'].sum()
    num_all = df['vol'].sum()
    num_avg = df['vol'].mean()
    diff = num_buy / num_all
    if diff > 0.7 :
        flag = True
    print(f'{code}  {flag}')
    return flag


def job_core():
    # 买入
    # stock_list = get_codes()
    # while True:
    #     my_df = get_speed(stock_list)
    #     for index, row in my_df.iterrows():
    #         flag = buy_strategy1(row['code'])
    #         if flag:
    #             current_balance = 55000
    #             buy_info(row['code'], row['price'], current_balance)
    #     time.sleep(3)

    # 卖出
    while True:
        sell_strategy1('127090')
        time.sleep(3)


if __name__ == '__main__':
    job_core()