import time

import pandas as pd

from mootdx.quotes import Quotes

from money import data_util

pd.set_option('mode.chained_assignment', None)
tdx_client = Quotes.factory(market='std')
dataframe = pd.read_excel('可转债.xlsx')

codes_before = []
codes_after = []
alert_data = []


# 获取股票
def get_stocks():
    codes = dataframe['代码']
    stock_list = []
    for code in codes.items():
        stock_list.append(str(code[1]))
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
    my_df = my_df[my_df['reversed_bytes9'] <= -0.5]
    # my_df = my_df[(my_df['reversed_bytes9'] >= 1) & (my_df['reversed_bytes9'] <= 5)]
    # 过滤涨幅
    # my_df = my_df[(my_df['price'] - my_df['last_close']) / my_df['last_close'] * 100 < 4]
    # 过滤当前价小于竞价
    # my_df = my_df[my_df['price'] > my_df['open']]
    # 按照Score列进行降序排序，并获取Top 3行
    # my_df = my_df.nlargest(10, 'reversed_bytes9')
    return my_df


# 买入策略1
def buy_strategy1(row):
    flag = False
    df = tdx_client.transaction(symbol=row.code, start=0, offset=100)
    price_max = df['price'].max()
    price = df['price'].values[-1]
    diff = round((price_max - price) / price * 100, 2)
    if diff > 2.5:
        alert_merge(row, diff)
        # name = dataframe[dataframe['代码'] == int(code)].values[0][1]
        # content = f'{code} {name} {diff}'
        # data_util.wx_push(content)
    return flag


def alert_merge(row, diff):
    current_timestamp = int(time.time())
    key_to_find = 'code'
    # 使用列表推导式查找键对应的值
    values = [item[key_to_find] for item in alert_data if key_to_find in item]
    if row['code'] in values:
        for item in alert_data:
            if item['code'] == row['code']:
                ts = item['ts']
                if current_timestamp - ts > 4 * 60:
                    name = dataframe[dataframe['代码'] == int(row.code)].values[0][1]
                    content = f'{row.code} {name} {diff}'
                    data_util.wx_push(content)
                    # 移除旧值
                    alert_before = {'code': row['code'], 'ts': ts}
                    alert_data.remove(alert_before)
                    alert = {'code': row['code'], 'ts': current_timestamp}
                    alert_data.append(alert)
                    break
            else:
                continue
    else:
        name = dataframe[dataframe['代码'] == int(row.code)].values[0][1]
        content = f'{row.code} {name} {diff}'
        data_util.wx_push(content)
        alert = {'code': row['code'], 'ts': current_timestamp}
        alert_data.append(alert)


if __name__ == '__main__':
    stock_list = get_stocks()
    while True:
        my_df = get_speed(stock_list)
        for index, row in my_df.iterrows():
            # diff = round((row.high - row.price) / row.price * 100, 2)
            # if diff > 6:
            #     alert_merge(row, diff)
            buy_strategy1(row)
        time.sleep(3)