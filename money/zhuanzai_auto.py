import time

from mootdx.quotes import Quotes

import easytrader
from datetime import datetime


tdx_client = Quotes.factory(market='std')
# 初始化账号
user = easytrader.use('eastmoney')
user.prepare('account.json')

# ==================================================================
code = "123056"
cb_price = 120
enable_amount = 950
min_price = cb_price
max_price = cb_price
k = 0
# 卖出标记
sell_flag = False
# ==================================================================


def get_price(code):
    df = tdx_client.quotes(symbol=[code])
    return df['price']


def sell(code, gd_price, enable_amount):
    user.sell(code, price=gd_price, amount=enable_amount)


def is_data(dq_price):
    global k, min_price, max_price
    if dq_price < min_price:
        min_price = dq_price
        k = k + 1
    if dq_price > max_price:
        max_price = dq_price
        k = 0
    if k == 1:
        return True
    return False


def sell_strategy(code, cb_price, enable_amount):
    global sell_flag
    dq_price = get_price(code)[0]
    zf = (dq_price - cb_price) / cb_price * 100

    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")

    print(f'时间：{formatted_time}  代码：{code}  涨幅：{zf}')
    if zf > 1:
        sell_flag = True
    if sell_flag and is_data(dq_price):
        gd_price = dq_price * 0.998
        sell(code, gd_price, enable_amount)
        return True
    # 割肉
    if zf <= -3:
        gd_price = dq_price * 0.998
        sell(code, gd_price, enable_amount)
        return True


if __name__ == '__main__':
    while True:
        flag = sell_strategy(code, cb_price, enable_amount)
        if flag:
            break
        time.sleep(2)