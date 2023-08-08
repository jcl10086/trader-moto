import time

import pandas as pd
from pytdx.hq import TdxHq_API

api = TdxHq_API()
with api.connect('119.147.212.81', 7709):

    # my_dicts = api.get_security_quotes([(0, '128081')])
    # my_dicts = api.get_security_quotes([(1, str(i)) for i in range(110058, 120060)])
    # for my_dict in my_dicts:
    #     for key, value in my_dict.items():
    #         if key == "code":
    #             print(str(value))

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

        batch_size = 80
        for i in range(0, len(stock_list), batch_size):
            my_dicts = api.get_security_quotes(stock_list[i:i + batch_size])
            for my_dict in my_dicts:
                for key, value in my_dict.items():
                    if key == "code":
                        print(str(value))
                    if key == "reversed_bytes9":
                        print("===" + str(value))

        time.sleep(4)
