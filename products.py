import pymysql
from os.path import exists

settings = {'host': '31.31.198.53',
            'database': 'u0752174_delfin_exchange',
            'user': 'u0752174_site_ex',
            'password': 'L7y7L1c6',
            'use_unicode': True}

con = pymysql.connect(**settings)
cur = con.cursor()

sql = '''select
	oc_product_description.product_id,
    oc_product_description.name,
    oc_product.image
from 
	oc_product_description, oc_product
where
	oc_product.product_id = oc_product_description.product_id and
    oc_product.image = '' and
	oc_product.product_id in
(
select distinct product_id from oc_product)'''

path = '\\\\srv-delfin\\Images\\Products\\'

cur.execute(sql)
res = cur.fetchall()
for i in res:
    product_id = str(i[0])
    dir_name = product_id[3:]
    file_name = path + dir_name + '\\' + product_id + '.jpg'
    is_exists = exists(file_name)
    if is_exists:
        bitrix_path = '%s/%s.jpg' % (dir_name, product_id)
        sql = 'update oc_product set image = "%s", date_action = 1 where product_id = %s' % (bitrix_path, product_id)
        cur.execute(sql)
        con.commit()
        print('Товару %s установлен путь %s' % (i[1], bitrix_path))
        print('Запрос: ', sql)
