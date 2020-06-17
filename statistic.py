import bitrix
# В модуле Битрикс есть подключение к БД
con = bitrix.connection
cur = bitrix.cursor

#   Получим список регионов
sql = 'select category_id, name from `u0752174_delfin_exchange`.`oc_store_category` where parent_id = 0 order by name'
try:
    cur.execute(sql)
except:
    print('Ошибка при запросе')
regions = cur.fetchall()
regions_list = {}
for region in regions:
    regions_list[region[0]] = region[1]
print("%-30s%-10s%-20.0s%-10s%-20.0s" % ('Регион', "Закрыто", "Сумма закрытых", "В обработке", "Сумма"))
for region in regions_list:
    sql_close = 'select count(TOTAL), sum(total) from `u0752174_delfin_exchange`.`oc_order_starta` where ID_SHOP in (select category_id from u0752174_delfin_exchange.oc_store_category where parent_id = %d) and LAST_STATE = 1' % region
    res = cur.execute(sql_close)
    closed_orders = cur.fetchone()
    if closed_orders[1] == None:
        closed_total = 0
    else:
        closed_total = float(closed_orders[1])
    sql_processed = 'select count(TOTAL) from `u0752174_delfin_exchange`.`oc_order_starta` where ID_SHOP in (select category_id from u0752174_delfin_exchange.oc_store_category where parent_id = %d) and Status_order = 0' % region
    res = cur.execute(sql_processed)
    processed_orders = cur.fetchone()
    sql_work = '''select 
	sum(product_sum)
from 
	u0752174_delfin_exchange.oc_order_products_starta 
    join u0752174_delfin_exchange.oc_order_starta on u0752174_delfin_exchange.oc_order_products_starta.ORDER_ID = u0752174_delfin_exchange.oc_order_starta.ORDER_ID
where 
	status_order = 0 and
	id_shop in
    (
		select category_id from u0752174_delfin_exchange.oc_store_category where parent_id = %d 
    )''' % region
    cur.execute(sql_work)
    res = cur.fetchone()
    if res[0] != None:
        work_total = float(res[0])
    else:
        work_total = 0
    print("%-30s%-10d%-20.0f%-10d%-20.0f" % (regions_list[region], closed_orders[0] , closed_total, processed_orders[0], work_total))
    f = open('report.csv', 'a')
    f.write("%s,%d,%f,%d,%f\n" % (regions_list[region], closed_orders[0] , closed_total, processed_orders[0], work_total))
    f.close()
