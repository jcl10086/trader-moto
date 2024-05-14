import time

import pandas as pd
import pymysql

conn = pymysql.connect(host='192.168.1.4', user='root', password='123456', cursorclass=pymysql.cursors.DictCursor)


def get_data():
    sql1 = ('SELECT `code`,MAX(price) AS max_value FROM data.online_data '
           'WHERE dt >= NOW() - INTERVAL 30 MINUTE GROUP BY `code`')
    cursor.execute(sql1)
    results1 = cursor.fetchall()

    sql2 = 'SELECT od1.code, od1.dt AS latest_dt, od1.price AS latest_price FROM data.online_data od1 INNER JOIN (SELECT code, MAX(dt) AS max_dt FROM data.online_data GROUP BY code) od2 ON od1.code = od2.code AND od1.dt = od2.max_dt'
    cursor.execute(sql2)
    results2 = cursor.fetchall()
    results = [{**d1, **d2} for d1 in results1 for d2 in results2 if d1['code'] == d2['code']]
    return results


def resolve_data(results):
    df = pd.DataFrame(results)
    df['latest_price'] = df['latest_price'].astype(float)
    df['max_value'] = df['max_value'].astype(float)
    df['zf'] = round((df['latest_price'] - df['max_value']) / df['max_value'] * 100, 2)
    df_new = df[df['zf'] <= -2]
    for index, row in df_new.iterrows():
        print(f'{row["code"]}===={row["latest_dt"]}===={row["zf"]}')
        print("")
        print("")
        print("")


if __name__ == '__main__':
    cursor = conn.cursor()
    while True:
        results = get_data()
        resolve_data(results)
        time.sleep(10)