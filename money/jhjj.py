import time
import urllib.request

import numpy as np
import pandas as pd
from scipy.stats import stats

dataframe = pd.read_excel('创业板.xlsx')


# 集合竞价
def get_codes():
    df_new = dataframe
    # df_new = dataframe[dataframe['涨幅%'].astype(float) < 3]
    codes = df_new['代码']
    stock_list = []
    for code in codes.items():
        stock_list.append(str(code[1]).zfill(6))
    return stock_list


# 获取竞价数据
def get_jj_data(code):
    url = 'https://16.push2.eastmoney.com/api/qt/stock/details/sse?fields1=f1,f4&fields2=f51,f52,' \
          'f53&pos=-0&secid=0.' + code
    with urllib.request.urlopen(url=url) as r:
        data = r.readline().decode().lstrip('data:')
    df = pd.DataFrame(eval(data)['data'])
    # 获取09:25:00索引
    if len(df['details']) == 0:
        return
    new_values = df[df['details'].str.contains('09:25:00', case=False)].index.values
    if len(new_values) == 0:
        return
    new_index = df[df['details'].str.contains('09:25:00', case=False)].index.values[0]
    if new_index <= 20:
        return
    df = df[0:new_index + 1]
    # 使用str.split()方法将列拆分成多列
    df[['datetime', 'price', 'num']] = df['details'].str.split(',', expand=True)
    # 删除原始的拆分列
    df.drop(columns=['details'], inplace=True)
    return df


def trend(df):
    # 计算每日竞价价格的变化
    # df['价格变化'] = df['price'].astype(float).diff()
    df = df[df['datetime'] >= '09:22:00']
    data = df['price'].astype(float).values

    # 计算80%的数据点数量
    threshold_percentage = 0.7
    threshold_count = int(len(data) * threshold_percentage)

    # 初始化一个计数器来记录符合条件的数据点数量
    count = 0

    # 遍历数据比较相邻数据点
    for i in range(1, len(data)):
        if data[i] > data[i - 1]:
            count += 1
            if count > threshold_count:
                print(f'{df["code"].values[0]}')
                # print(f"数组中至少80%的数据后的值大于前一个值")
                break
        else:
            count = 0  # 重置计数器

    # 如果没有找到符合条件的趋势
    # if count < threshold_count:
    #     print("数组中不足80%的数据后的值大于前一个值")


def trend1(df):
    data = df['price'].astype(float).values
    zf = round((data[-1] - data[-2]) / data[-2] * 100, 2)
    prePrice = df["prePrice"].values[0]
    if zf > 1 and data[-1] > float(prePrice):
        print(f'{df["code"].values[0]}')


if __name__ == '__main__':
    # code = '300621'
    # df = get_jj_data(code)
    # if df is not None:
    #     trend(df)
    codes = get_codes()
    # 记录开始时间
    start_time = time.time()
    for index, code in enumerate(codes):
        df = get_jj_data(code)
        if df is not None:
            trend1(df)
        # print(str(index + 1))
    # 记录结束时间
    end_time = time.time()

    # 计算执行时间
    execution_time = end_time - start_time

    print(f"代码执行时间为 {execution_time:.2f} 秒")