import math

import easytrader

user = easytrader.use('eastmoney')
user.prepare('account.json')
balance = str(user.balance[0])
start_index = balance.find("(") + 1  # 找到左括号的索引位置，并加1
end_index = balance.find(")")  # 找到右括号的索引位置
substring = balance[start_index:end_index]  # 使用切片操作截取两个括号之间的内容
substring = substring.split(",")[1]
# 可用资金 预留手续非
current_balance = float(substring.split("=")[1]) - 300
print(current_balance)

# 股票代码
code = '118021'
# 当前股价
current_price = 233.533
# 挂单股价
gd_price = current_price * 1.05
gd_price = round(gd_price, 2)
# 挂单数量
gd_num = math.floor(current_balance / gd_price / 10) * 10

# 买入
user.buy(code, price=gd_price, amount=gd_num)

print(user.position)


# 卖出
# user.sell('162411', price=0.55, amount=100)