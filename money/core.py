import re
import time

from pytdx.hq import TdxHq_API

import easytrader

user = None


def get_user():
    global user
    user = easytrader.use('eastmoney')
    user.prepare('account.json')


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
def buy_info():
    print()


# 获取持仓
# stock_code 代码  cost_price 成本价  enable_amount 可用数量
def position_info():
    positions = user.position
    enable_amount = 0
    for position in positions:
        # 使用正则表达式解析字符串
        pattern = r"(\w+)\s*=\s*([\w.'\d]+)"
        matches = re.findall(pattern, str(position))
        for match in matches:
            if match[0] == 'enable_amount':
                enable_amount = int(match[1])
            if match[0] == 'stock_code':
                stock_code = eval(match[1])
            if match[0] == 'cost_price':
                cost_price = eval(match[1])
        if enable_amount != 0:
            break
    if enable_amount != 0:
        my_position = {'stock_code': stock_code, 'cost_price': cost_price, 'enable_amount': enable_amount}
        # print(my_position)
        return my_position
    else:
        return None


# 挂单卖出
def sell_info():
    my_position = position_info()
    if my_position is not None:
        online_one_price(my_position)


# 获取个股实时价格
def online_one_price(my_position):
    stock_code = my_position['stock_code']
    cost_price = my_position['cost_price']
    enable_amount = my_position['enable_amount']

    api = TdxHq_API()
    with api.connect('119.147.212.81', 7709):
        # 判断市场代码
        market_code = 0
        my_dicts = api.get_security_quotes([(market_code, stock_code)])
        if my_dicts is None:
            market_code = 1

        # 当前最大价
        max_price = 0.0
        while True:
            flag = True
            my_dicts = api.get_security_quotes([(market_code, stock_code)])
            for my_dict in my_dicts:
                for key, value in my_dict.items():
                    if key == "price":
                        # 现价
                        price = round(float(value) / 100, 3)
                        diff_yk = round((price - cost_price) / cost_price * 100, 2)
                        print('现价：' + str(price) + ', 成本价：' + str(cost_price), ', 盈亏：' + str(diff_yk))

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

                        # 止损价 -1%
                        if price <= cost_price * 0.99:
                            gd_price = round(cost_price * 0.95, 2)
                            # 挂 -5% 清仓
                            user.sell(stock_code, price=gd_price, amount=enable_amount)
                            print('止损')
                            flag = False
                            break
                        break
            if flag is False:
                break
            time.sleep(3)


# def test():
#     user.sell('123177', price=100, amount=10)


if __name__ == '__main__':
    get_user()
    # print(str(get_balance()))
    # position_info()
    # online_one_price('')
    sell_info()
    # test()
