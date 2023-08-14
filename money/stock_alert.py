import pandas as pd
from mootdx.quotes import Quotes

client = Quotes.factory(market='std')

dataframe = pd.read_excel('可转债.xlsx')
codes = dataframe['转债代码']

stock_list = []
for code in codes.items():
    stock_list.append(code[1].split('.')[0])

merged_df = None
batch_size = 80
for i in range(0, len(stock_list), batch_size):
    df = client.quotes(symbol=stock_list[i:i + batch_size])
    merged_df = pd.concat([merged_df, df], ignore_index=True)

# 删选出当日最大涨幅大于3%
merged_df = merged_df[(merged_df['high'] - merged_df['last_close']) / merged_df['last_close'] > 0.03].reset_index()
# 最大价格与当前价格差值
merged_df['diff'] = (merged_df['high'] - merged_df['price']) / merged_df['price']
merged_df = merged_df.sort_values(by='diff', ascending=False).reset_index()

for row in merged_df.itertuples():
    diff = round(row.diff * 100, 2)
    print(f'{row.code}：差值空间{diff}%')