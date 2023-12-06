import time
from datetime import datetime
from queue import Queue

import pywencai

from money import data_util


def get_codes():
    stock_list = []
    res = pywencai.get(query='沪深主板非st，最大涨幅>6，分时涨速>0.8，大单净量>8', sort_key='最新涨跌幅', sort_order='desc')
    if res is not None:
        stock_list = res['code'].values.tolist()
    return stock_list


def job(q):
    codes = get_codes()
    # 写入
    for code in codes:
        q.put(code)

    # 不停地输出，直到队列为空
    while not q.empty():
        content = q.get()
        if content not in q_history.queue:
            data_util.wx_push(content)
            # 记录历史
            q_history.put(content)
            current_time = datetime.now()
            formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
            print(f"{formatted_time}  {content}")


if __name__ == '__main__':
    # 创建一个队列
    q = Queue()
    q_history = Queue()
    while True:
        job(q)
        time.sleep(15)