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

dataframe = pd.read_excel('创业板.xlsx')


def get_codes():
    df_new = dataframe[dataframe['涨幅%'].astype(float) < 3]
    codes = df_new['代码']
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
    my_df = my_df[(1 <= my_df['reversed_bytes9']) & (my_df['reversed_bytes9'] <= 4)]
    # 过滤涨幅
    # my_df['zf'] = (my_df['price'] - my_df['last_close']) / my_df['last_close'] * 100
    my_df['zf'] = my_df.apply(lambda row: round((row['price'] - row['last_close']) / row['last_close'] * 100, 2), axis=1)
    my_df = my_df[(3.5 > my_df['zf']) & (my_df['zf'] > -4)]
    # 过滤当前价小于竞价
    # my_df = my_df[my_df['price'] > my_df['open']]
    # 按照Score列进行降序排序，并获取Top 3行
    my_df = my_df.nlargest(10, 'reversed_bytes9')
    return my_df


# 买入策略1
def buy_strategy1(code):
    # 阈值平均量
    num_flag = 0
    flag = False
    df = tdx_client.transaction(symbol=code, start=0, offset=200)
    df_begin = df[1:20]
    df = df[-20:]
    num_begin = df_begin['vol'].sum()
    num_now = df['vol'].sum()
    num_buy = df[df['buyorsell'] == 0]['vol'].sum()
    num_sell = df[df['buyorsell'] == 1]['vol'].sum()
    num_all = num_buy + num_sell
    num_avg = num_all / len(df)
    diff = num_buy / num_all

    # 总流通
    # nums = 1.32
    nums = dataframe[dataframe['代码'] == int(code)]['流通股(亿)'].values[0]
    if nums < 0.5:
        num_flag = 120
    elif 0.5 <= nums < 1:
        num_flag = 200
    elif 1 <= nums < 2:
        num_flag = 350
    elif 2 <= nums < 3:
        num_flag = 800
    else:
        num_flag = 1000
    if diff > 0.75 and num_avg > num_flag and num_now > 2 * num_begin:
        flag = True
        print(f'{code} {df[-1:]["time"].values[0]} {flag}')
    return flag


# 挂单买入
def buy_info(code, price, enable_balance):
    # 挂单股价
    gd_price = price * 1.02
    gd_price = round(gd_price, 2)
    # 挂单数量
    gd_num = math.floor(enable_balance / gd_price / 100) * 100
    print(f'挂单价格：{gd_price}  挂单数量：{gd_num}')
    # 买入
    user.buy(code, price=gd_price, amount=gd_num)
    return gd_num


def core_job():
    stock_list = get_codes()
    my_df = get_speed(stock_list)
    for index, row in my_df.iterrows():
        code = row['code']
        price = row['price']
        flag = buy_strategy1(code)
        if flag:
            enable_balance = 80000
            buy_info(code, price, enable_balance)
            break


if __name__ == '__main__':
    target_time = datetime.time(7, 30, 28)
    while True:
        current_time = datetime.datetime.now().time()
        if current_time >= target_time:
            core_job()
        time.sleep(3)