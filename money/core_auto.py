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


# 获取可用资金
def get_balance():
    balance = user.balance[0]
    # 可用资金  预留300
    enable_balance = balance.enable_balance - 300
    return enable_balance


# 获取持仓
# stock_code 代码  cost_price 成本价  enable_amount 可用数量
def position_info():
    positions = user.position
    positions_new = []
    for position in positions:
        if position.enable_amount > 0:
            positions_new.append(position)
            break
    return positions_new


# 挂单买入
def buy_info(code, price, enable_balance):
    # 挂单股价
    gd_price = price * 1.03
    gd_price = round(gd_price, 2)
    # 挂单数量
    gd_num = math.floor(enable_balance / gd_price / 10) * 10
    print(f'挂单价格：{gd_price}  挂单数量：{gd_num}')
    # 买入
    user.buy(code, price=gd_price, amount=gd_num)
    return gd_num


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
    my_df = my_df[(my_df['reversed_bytes9'] >= 0.3) & (my_df['reversed_bytes9'] <= 1.5)]
    # 过滤涨幅
    # my_df = my_df[(my_df['price'] - my_df['last_close']) / my_df['last_close'] * 100 < 5]
    # 按照Score列进行降序排序，并获取Top 3行
    # my_df = my_df.nlargest(10, 'reversed_bytes9')
    return my_df


# 买入策略1
def buy_strategy1(code):
    flag = False
    df = tdx_client.transaction(symbol=code, start=0, offset=10)
    price_max = df['price'].max()
    price_last = df['price'][-1:]
    # df = df[0:38]
    diff = round((df['price'][len(df) - 1] - df['price'][0]) / df['price'][0] * 100, 2)
    avg_vol = df['vol'].mean()
    if diff > 0.3 and avg_vol > 200 and price_max == price_last:
        flag = True
    return flag


# 卖出策略2
def sell_strategy2(code, cb_price, enable_amount):
    flag = False
    high = 0
    # 阈值价 止损0.5%
    fz_price = cb_price * 0.995
    # 挂单价
    gd_price = round(cb_price * 0.9, 2)
    while True:
        df = tdx_client.quotes(symbol=code)
        price = round(df['price'].values[0], 2)
        if high < price:
            high = price

        # 涨0.5%  阈值0.3%
        # if price > cb_price * 1.005:
        #     fz_price = cb_price * 1.003
        # 涨1%  阈值0.5%
        if price > cb_price * 1.01:
            fz_price = cb_price * 1.005
        # 涨1% - 1.5% 阈值1%
        # if cb_price * 1.015 >= price > cb_price * 1.01:
        #     fz_price = cb_price * 1.01
        if price > cb_price * 1.015:
            fz_price = high * 0.985

        fz_price = round(fz_price, 2)
        yk = round((price - cb_price) / cb_price * 100, 2)
        if price < fz_price:
            user.sell(code, price=gd_price, amount=enable_amount)
            flag = True
        print(f'{code} {price} {yk}%  清仓：{flag}')
        if flag:
            break
        time.sleep(3)


def core_job():
    stock_list = get_codes()
    # 获取持仓
    positions = position_info()
    if len(positions) == 0:
        flag = False
        while True:
            my_df = get_speed(stock_list)
            for index, row in my_df.iterrows():
                code = row['code']
                price = row['price']
                flag = buy_strategy1(code)
                if flag:
                    enable_balance = get_balance()
                    buy_info(code, price, enable_balance)
                    break
            if flag:
                break
            time.sleep(3)
    # 重新获取仓位
    positions = position_info()
    if len(positions) == 0:
        return
    position = positions[0]
    code = position.stock_code
    cb_price = position.cost_price
    enable_amount = position.enable_amount
    sell_strategy2(code, cb_price, enable_amount)


if __name__ == '__main__':
    while True:
        core_job()