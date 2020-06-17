import pymysql
from os.path import exists

settings = {'host': '31.31.198.53',
            'database': 'u0752174_delfin_exchange',
            'user': 'u0752174_site_ex',
            'password': 'L7y7L1c6',
            'use_unicode': True}

con = pymysql.connect(**settings)
cur = con.cursor()

def get_shop_id_by_name(name):
    sql = 'select category_id from oc_store_category where name like "%s"' % name
    try:
        cur.execute(sql)
        return int(cur.fetchone()[0])
    except Exception as e:
        print('Ошибка при получении имени\n',e)


print(get_shop_id_by_name('ФКУ Исправительная колония №20 (Лу%'))