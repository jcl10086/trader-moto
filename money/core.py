import datetime
import math
import re
import time

import numpy as np
import pandas as pd
import pymysql
import redis

from pytdx.hq import TdxHq_API

import easytrader

# 初始化账号
user = easytrader.use('eastmoney')
user.prepare('account.json')

# 创建API对象
api = TdxHq_API()
# 连接到行情服务器
api.connect('119.147.212.81', 7709)

# 连接到Redis
r = redis.Redis(host='192.168.1.4', port=6379, db=0)


# 获取可以资金
def get_balance():
    balance = user.balance[0]
    # 使用正则表达式解析字符串
    pattern = r"(\w+)\s*=\s*([\w.'\d]+)"
    matches = re.findall(pattern, str(balance))
    for match in matches:
        if match[0] == 'current_balance':
            # 预留300作为手续费
            current_balance = float(match[1]) - 300
            return current_balance


# 挂单买入
def buy_info(code, current_price, current_balance):
    # 挂单股价
    gd_price = current_price * 1.05
    gd_price = round(gd_price, 2)
    # 挂单数量
    gd_num = math.floor(current_balance / gd_price / 10) * 10
    # 买入
    user.buy(code, price=gd_price, amount=gd_num)
    return gd_num


# 获取当日成交
def current_deal_info():
    # 获取最新买入 stock_code 代码  cost_price 成本价  enable_amount 可用数量
    current_deal = user.current_deal[0]
    if current_deal.bs_type == 'B':
        stock_code = current_deal.stock_code
        cost_price = current_deal.deal_price
        enable_amount = current_deal.deal_amount
        my_position = {'stock_code': stock_code, 'cost_price': cost_price, 'enable_amount': enable_amount}
        return my_position


# 获取持仓
# stock_code 代码  cost_price 成本价  enable_amount 可用数量
# def position_info():
#     positions = user.position
#     enable_amount = 0
#     for position in positions:
#         # 使用正则表达式解析字符串
#         pattern = r"(\w+)\s*=\s*([\w.'\d]+)"
#         matches = re.findall(pattern, str(position))
#         for match in matches:
#             if match[0] == 'enable_amount':
#                 enable_amount = int(match[1])
#             if match[0] == 'stock_code':
#                 stock_code = eval(match[1])
#             if match[0] == 'cost_price':
#                 cost_price = eval(match[1])
#         if enable_amount != 0:
#             break
#     if enable_amount != 0:
#         my_position = {'stock_code': stock_code, 'cost_price': cost_price, 'enable_amount': enable_amount}
#         # print(my_position)
#         return my_position
#     else:
#         return None


def get_stock_top():
    dataframe = pd.read_excel('可转债.xlsx')
    codes = dataframe['转债代码']
    while True:
        stock_list = []
        for code in codes.items():
            # xx.SZ  xx.SH
            if code[1].split('.')[1] == 'SZ':
                stock_list.append((0, str(code[1].split('.')[0])))
            elif code[1].split('.')[1] == 'SH':
                stock_list.append((1, str(code[1].split('.')[0])))
            else:
                continue
        # stock_list = [(0, '123205')]
        my_dict_all = []
        batch_size = 80
        for i in range(0, len(stock_list), batch_size):
            my_dicts = api.get_security_quotes(stock_list[i:i + batch_size])
            for my_dict in my_dicts:
                data_dict = {'reversed_bytes9': my_dict['reversed_bytes9'], 'code': my_dict['code'], 'price': my_dict['price']}
                my_dict_all.append(data_dict)
        my_df = pd.DataFrame(my_dict_all)
        # 过滤条件：reversed_bytes0
        my_df = my_df[(my_df['reversed_bytes9'] >= 0.6) & (my_df['reversed_bytes9'] <= 2)]
        # 按照Score列进行降序排序，并获取Top 3行
        my_df = my_df.nlargest(3, 'reversed_bytes9')
        # 遍历指定的列
        for index, row in my_df.iterrows():
            flag = check_data(row['code'])
            if flag:
                current_price = round(row['price'] / 100, 2)
                current_balance = get_balance()
                # 买入数量
                gd_num = buy_info(row['code'], current_price, current_balance)
                time.sleep(1)
                # 卖
                sell_info(gd_num)
                break
        time.sleep(3)


# 校验数据 取最近5个值 判断是否程上升趋势
def check_data(code):
    flag = False
    # 模糊查询键值对
    keys = r.scan_iter(match=f'order:{code}*')

    # 获取匹配的键值对
    result = []
    for key in keys:
        data = r.hgetall(key.decode())
        # 将字节字符串转换为Unicode字符串
        data = {key.decode(): value.decode() for key, value in data.items()}
        result.append(data)
    if len(result) == 0:
        return flag
    my_df = pd.DataFrame(result)
    # 按照reversed_bytes0列进行升序排序
    my_df = my_df.sort_values('reversed_bytes0')
    # 获取最近的5个值
    my_df = my_df.tail(5)

    # 将price列转换为数组  价格
    price_array = my_df['price'].values.astype(float)
    # 判定数组增长趋势
    threshold = 0.6
    flag1 = is_data_increasing(price_array, threshold)

    # cur_vol列转换为数组  当前成交量
    vol_array = my_df['cur_vol'].values.astype(int)
    flag2 = False
    if round(np.mean(vol_array)) > 300:
        flag2 = True

    if flag1 & flag2:
        flag = True
    return flag


# 判断数据大体上涨
def is_data_increasing(data, threshold):
    count = 0
    for i in range(1, len(data)):
        if data[i] > data[i-1]:
            count += 1
    ratio = count / len(data)
    if ratio >= threshold:
        return True
    else:
        return False


# 挂单卖出
def sell_info(gd_num):
    my_position = current_deal_info()

    if my_position is not None:
        # 判断是否有挂单
        if gd_num > 0:
            my_position['enable_amount'] = gd_num
        online_one_price(my_position)


# 获取个股实时价格
def online_one_price(my_position):
    stock_code = my_position['stock_code']
    cost_price = my_position['cost_price']
    enable_amount = my_position['enable_amount']

    # 判断市场代码
    market_code = 0
    my_dicts = api.get_security_quotes([(market_code, stock_code)])
    if my_dicts is None:
        market_code = 1

    # 保本价
    bb_price = 0.0
    # 当前最大价
    max_price = 0.0
    while True:
        flag = True
        my_dicts = api.get_security_quotes([(market_code, stock_code)])
        for my_dict in my_dicts:
            data_dict = dict(my_dict)
            price = data_dict['price']
            # 现价
            price = round(float(price) / 100, 3)
            diff_yk = round((price - cost_price) / cost_price * 100, 2)
            print('现价：' + str(price) + ', 成本价：' + str(cost_price), ', 盈亏：' + str(diff_yk))

            # # 设置保本价格
            if price > cost_price * 1.006 and bb_price == 0.0:
                bb_price = 1.002 * cost_price

            # 设置最大价格
            if price > cost_price * 1.015 and max_price == 0.0:
                max_price = price
                print('触发最大价===========================================')

            if price > max_price != 0.0:
                max_price = price

            # 最大价格以激活 止盈 1%
            if max_price != 0.0:
                if price <= cost_price * 1.01:
                    gd_price = round(cost_price * 0.95, 2)
                    # 挂 -5% 清仓
                    user.sell(stock_code, price=gd_price, amount=enable_amount)
                    print('止盈')
                    flag = False
                    break
                # 差价涨幅
                diff_zf = round((max_price - price) / price * 100, 2)
                if diff_zf > 1.5:
                    gd_price = round(cost_price * 0.95, 2)
                    # 挂 -5% 清仓
                    user.sell(stock_code, price=gd_price, amount=enable_amount)
                    print('止盈')
                    flag = False
                    break

            # 保本0.002
            if price <= bb_price != 0.0:
                gd_price = round(cost_price * 0.95, 2)
                # 挂 -5% 清仓
                user.sell(stock_code, price=gd_price, amount=enable_amount)
                print('保本')
                flag = False
                break

            # 止损价 -0.8%
            if price <= cost_price * 0.992:
                gd_price = round(cost_price * 0.95, 2)
                # 挂 -5% 清仓
                user.sell(stock_code, price=gd_price, amount=enable_amount)
                print('止损')
                flag = False
                break

        if flag is False:
            break
        time.sleep(3)


# def test():
#     # user.current_deal
#     data = api.get_transaction_data(0, '123205', start=0, count=10)  # 获取最新的10笔交易数据


if __name__ == '__main__':
    get_stock_top()
    # sell_info(0)

