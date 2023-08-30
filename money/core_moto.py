# 买入策略
import datetime
import math
import time

import pandas as pd

from mootdx.quotes import Quotes

import easytrader

tdx_client = Quotes.factory(market='std')
# 初始化账号
user = easytrader.use('eastmoney')
user.prepare('account.json')


def get_codes():
    dataframe = pd.read_excel('可转债.xlsx')
    codes = dataframe['代码']

    stock_list = []
    for code in codes.items():
        stock_list.append(str(code[1]).zfill(6))
    return stock_list


# 获取涨速
def get_speed(stock_list):
    # stock_list = stock_list[0:1200]
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
    my_df = my_df[(my_df['price'] - my_df['last_close']) / my_df['last_close'] * 100 < 5]
    # 按照Score列进行降序排序，并获取Top 3行
    my_df = my_df.nlargest(10, 'reversed_bytes9')
    return my_df


# 买入策略1
def buy_strategy1(code):
    flag = False
    df = tdx_client.transaction(symbol=code, start=0, offset=12)
    num_buy = df[df['buyorsell'] == 0]['vol'].sum()
    num_all = df['vol'].sum()
    num_avg = df['vol'].mean()
    diff = num_buy / num_all
    if diff > 0.7 and num_avg > 300:
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
    user.buy(code, price=gd_price, amount=gd_num)
    return gd_num


# 卖出策略1
def sell_strategy1(code, gd_price, enable_amount):
    flag = False
    df = tdx_client.transaction(symbol=code, start=0, offset=40)
    num_sell = df[df['buyorsell'] == 1]['vol'].sum()
    num_all = df['vol'].sum()
    # num_avg = df['vol'].mean()
    diff = num_sell / num_all
    if diff > 0.8:
        # 获取当前时间对象
        current_time = datetime.now()
        # 指定要使用的时间格式
        time_format = "%Y-%m-%d %H:%M:%S"  # 例如："2023-08-28 15:30:00"
        # 将时间对象格式化为字符串
        formatted_time = current_time.strftime(time_format)
        # 挂 -5% 清仓
        # user.sell(code, price=gd_price, amount=enable_amount)
        flag = True
        print(f'{formatted_time}  {code}  {flag}')
    return flag


def job_core():
    # 买入
    stock_list = get_codes()
    while True:
        my_df = get_speed(stock_list)
        for index, row in my_df.iterrows():
            flag = buy_strategy1(row['code'])
            if flag:
                current_balance = 113000
                buy_info(row['code'], row['price'], current_balance)
        time.sleep(3)

    # 卖出
    # while True:
    #     sell_strategy1('123200', '200', '560')
    #     time.sleep(3)


if __name__ == '__main__':
    job_core()