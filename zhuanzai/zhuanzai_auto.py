import time

from mootdx.quotes import Quotes

import easytrader
from datetime import datetime

tdx_client = Quotes.factory(market='std')
# 初始化账号
user = easytrader.use('eastmoney')
user.prepare('account.json')

# ==================================================================
code = "123034"
cb_price = 242.829
enable_amount = 870
min_price = 1000
max_price = 0
k = 0
# 卖出标记
sell_flag_one = False
sell_flag_two = False
# 保本
sell_flag_bb1 = False
sell_flag_bb2 = False
# ==================================================================


def get_price(code):
    df = tdx_client.quotes(symbol=[code])
    return df['price']


def sell(code, gd_price, enable_amount):
    user.sell(code, price=gd_price, amount=enable_amount)


def is_data_one(dq_price):
    global k, min_price, max_price
    if dq_price < min_price:
        min_price = dq_price
        k = k + 1
    if dq_price > max_price:
        max_price = dq_price
        min_price = dq_price
        k = 0
    if k == 4:
        return True
    return False


def is_data_two(dq_price):
    global k, min_price, max_price
    if dq_price < min_price:
        min_price = dq_price
        k = k + 1
    if dq_price > max_price:
        max_price = dq_price
        min_price = dq_price
        k = 0
    if k == 7:
        return True
    return False


def sell_strategy(code, cb_price, enable_amount):
    global sell_flag_one
    global sell_flag_two
    global sell_flag_bb1
    global sell_flag_bb2
    dq_price = get_price(code)[0]
    zf = round((dq_price - cb_price) / cb_price * 100, 2)

    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    if zf > 0.8:
        sell_flag_one = True
    if zf > 1.8:
        sell_flag_two = True
    if zf <= -1.5:
        sell_flag_bb1 = True
    if dq_price >= cb_price and sell_flag_bb1:
        sell_flag_bb2 = True
    if sell_flag_one and is_data_one(dq_price) and not sell_flag_two:
        gd_price = round(dq_price * 0.998, 2)
        sell(code, gd_price, enable_amount)
        return True
    if sell_flag_two and is_data_two(dq_price):
        gd_price = round(dq_price * 0.998, 2)
        sell(code, gd_price, enable_amount)
        return True
    if sell_flag_bb2:
        if dq_price < cb_price * 1.005:
            gd_price = round(dq_price * 0.998, 2)
            sell(code, gd_price, enable_amount)
            return True
    # 割肉
    if zf <= -3:
        gd_price = round(dq_price * 0.998, 2)
        sell(code, gd_price, enable_amount)
        return True
    print(f'时间：{formatted_time}  代码：{code}  现价：{round(dq_price, 2)}  涨幅：{zf} 计数：{k} 最小值：{round(min_price, 2)} 最大值：{round(max_price, 2)}')


if __name__ == '__main__':
    while True:
        flag = sell_strategy(code, cb_price, enable_amount)
        if flag:
            break
        time.sleep(2)
