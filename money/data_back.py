import pandas as pd
from mootdx.quotes import Quotes

tdx_client = Quotes.factory(market='std')


def get_data_by_code(code):
    merged_df = None
    batch_sizes = [0, 2000, 4000]
    for batch_size in batch_sizes:
        df = tdx_client.transactions(symbol=code, start=batch_size, offset=2000, date='20230823')
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
    if diff > 0.8 and num_avg > 500:
        flag = True
        print(f'{code} {df[-1:]["time"].values[0]} {flag}')
    return flag


def core_job(code):
    my_df = get_data_by_code(code)
    for i in range(13, len(my_df) - 1):
        df = my_df[1:i]
        buy_strategy1(code, df)


def get_codes():
    dataframe = pd.read_excel('股票1.xlsx')
    codes = dataframe['代码']

    stock_list = []
    for code in codes.items():
        stock_list.append(str(code[1]))
    return stock_list


if __name__ == '__main__':
    # code = '002750'
    # core_job(code)

    codes = get_codes()
    for code in codes:
        core_job(code)
        print()
        print()
        print()