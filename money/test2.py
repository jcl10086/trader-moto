import time

from pytdx.hq import TdxHq_API

api = TdxHq_API()
with api.connect('119.147.212.81', 7709):

    # 获取实时行情数据
    while True:
        data = api.get_security_quotes([(1, str(i)) for i in range(110058, 110060)])
        # data = api.get_security_quotes([(1, '110059')])
        # print(data)
        start_index = str(data).find("[OrderedDict([") + len("[OrderedDict([") - 1  # 找到左括号的索引位置，并加1
        end_index = str(data).find("])]") + 1  # 找到右括号的索引位置
        substring = str(data)[start_index:end_index]  # 使用切片操作截取两个括号之间的内容
        data_list = eval(substring)
        price = round(data_list[3][1] / 100, 2)
        speed = data_list[43][1]
        print(str(price) + "===" + str(speed))
        time.sleep(3)

