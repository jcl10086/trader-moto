import pandas as pd
from mootdx.quotes import Quotes

tdx_client = Quotes.factory(market='std')
high = 0
low = 10000
# 计数
num = 0
dataframe = pd.read_excel('可转债.xlsx')


def get_data_by_code(code):
    merged_df = None
    batch_sizes = [0, 2000, 4000]
    for batch_size in batch_sizes:
        df = tdx_client.transactions(symbol=code, start=batch_size, offset=2000, date='20230905')
        # df = tdx_client.transaction(symbol=code, start=batch_size, offset=2000)
        merged_df = pd.concat([df, merged_df], ignore_index=True)
    return merged_df


# 买入策略1
def buy_strategy1(code, df):
    df = df[-12:]
    flag = False
    # df = tdx_client.transaction(symbol=code, start=0, offset=20)
    num_buy = df[df['buyorsell'] == 0]['vol'].sum()
    num_all = df['vol'].sum()
    num_avg = df['vol'].mean()
    diff = num_buy / num_all
    if diff > 0.8 and num_avg > 400:
        flag = True
        print(f'{code} {df[-1:]["time"].values[0]} {flag}')
    return flag


# 买入策略1
def buy_strategy2(code, df):
    df_before = df
    df = df[-10:]
    flag = False
    # df = tdx_client.transaction(symbol=code, start=0, offset=12)
    num_buy = df[df['buyorsell'] == 0]['vol'].sum()
    num_sell = df[df['buyorsell'] == 1]['vol'].sum()
    num_all = num_buy + num_sell
    num_avg = num_all / len(df)
    diff = num_buy / num_all

    # 总流通
    nums = 1.32
    # nums = dataframe[dataframe['代码'] == int(code)]['流通股(亿)'].values[0]
    if nums < 1.2:
        num_flag = 120
    elif 1.2 <= nums < 2.5:
        num_flag = 400
    else:
        num_flag = 1000
    if diff > 0.8 and num_avg > num_flag and df['price'].values[-1] > df_before['price'].values[0]:
        flag = True
        print(f'{code} {df[-1:]["time"].values[0]} {flag}')
    return flag


# 买入策略1
def buy_strategy3(code, df):
    # num_avg = 0
    df = df[1:11]
    flag = False
    # df = tdx_client.transaction(symbol=code, start=0, offset=12)
    # num_buy = df[df['buyorsell'] == 0]['vol'].sum()
    # num_sell = df[df['buyorsell'] == 1]['vol'].sum()
    # num_all = num_buy + num_sell
    # num_avg = num_all / len(df)
    # diff = num_buy / num_all
    diff = (df['price'].values[-1] - df['price'].values[0]) / df['price'].values[0]
    diff = round(diff * 100, 2)
    num_avg = df['vol'].mean()

    # 总流通
    nums = dataframe[dataframe['代码'] == int(code)]['流通股(亿)'].values[0]
    if nums < 1.2:
        num_flag = 120
    elif 1.2 <= nums < 2.5:
        num_flag = 400
    else:
        num_flag = 1000
    if diff > 1.5 and num_avg > num_flag:
        flag = True
        print(f'{code} {df[-1:]["time"].values[0]} {flag}')
    return flag


def sell_strategy1(code, df):
    df = df[-30:]
    num_sell = df[df['buyorsell'] == 1]['vol'].sum()
    num_all = df['vol'].sum()
    # num_avg = df['vol'].mean()
    diff = num_sell / num_all
    if diff > 0.7:
        print(f'{code} {df[-1:]["time"].values[0]}')


def sell_strategy2(code, df):
    df = df[-40:]
    high = 0
    low = 10000
    i = 0
    for index, row in df.iterrows():
        price = row['price']
        if high < price:
            high = price
            low = high
            i = 0
        else:
            if price < low:
                low = price
                i = i + 1
            if i == 5:
                ts = row['time']
                print(f'{code} {ts} {price}')
    # num_sell = df[df['buyorsell'] == 1]['vol'].sum()
    # num_all = df['vol'].sum()
    # # num_avg = df['vol'].mean()
    # diff = num_sell / num_all
    # if diff > 0.7:
    #     print(f'{code} {df[-1:]["time"].values[0]}')


def sell_strategy3(code, df):
    high = 0
    i = 0
    for index, row in df.iterrows():
        price = row['price']
        if high <= price:
            high = price
            i = 0
            ts = row['time']
        else:
            i = i + 1
        if i == 40:
            print(f'{code} {ts} {price}')
            high = 0
            i = 0


def sell_strategy4(code, df):
    price = df['price'].values[0]
    global high, low
    if high <= price:
        high = price
    if low >= price:
        low = price
    print()


def core_job(code):
    my_df = get_data_by_code(code)
    # buy_strategy3(code, my_df)
    for i in range(11, len(my_df) - 1):
        df = my_df[0:i]
        buy_strategy2(code, df)
    #     sell_strategy2(code, df)
    # df = my_df[1:200]
    # df = my_df
    # sell_strategy4(code, df)


def get_codes():
    codes = dataframe['代码']

    stock_list = []
    for code in codes.items():
        stock_list.append(str(code[1]))
    return stock_list


if __name__ == '__main__':
    # code = '300538'
    # core_job(code)

    codes = get_codes()
    for code in codes:
        core_job(code)
        print()
        print()
        print()