import bitrix
import xlwt
# Получим список закрытых заказов
sql = '''
select 
	ORDER_ID,
    TOTAL
from 
	u0752174_delfin_exchange.oc_order_starta
where
	LAST_STATE = 1 and
    STATUS_ORDER = 3 and
    ORDER_ID > 122 and
    ORDER_ID IN (
        SELECT order_id FROM u0752174_delfin_exchange.Checks where date (date_time) between "2020-08-25
        " and "2020-09-15")
    '''
bitrix.cursor.execute(sql)
res = bitrix.cursor.fetchall()
counter = 1
sbr_result = 0
check_result = 0
print('%s;%s;%s;%s;%s;%s;%s;%s;%s' % ('№', 'Регион', 'Магазин', 'Номер заказа', 'Сумма ДиФ', 'Сумма строки', 'Сумма Сбер',
                                             'Сумма чек', 'Контроль'))
file_name = 'buh_report.csv'
f = open(file_name, 'a', encoding='utf-8')
for i in res:
    order_id = i[0]
    total_oc_order = i[1]
    a = bitrix.Order(order_id)
    region = a.region
    store = a.store
    total_pos = a.total
    if len(a.checks) !=0:
        date_of_check = a.checks[0].date
        check_total = a.checks[0].total
        check_result += check_total
    else:
        date_of_check = None
        check_total = 0
    sbr_total = a.payment.finish_sum
    sbr_result += sbr_total
    auth_code = a.payment.transaction
    testing = (total_pos + check_total + sbr_total) / 3
    if testing - total_pos == 0:
        control = 0
    else:
        control = 1
    print('%d;%s;%s;%d;%f;%f;%f;%f;%d;%s;%s' % (counter, region, store,  order_id, total_oc_order, total_pos, sbr_total,
                                                          check_total, control, date_of_check, auth_code))
    f.write('%d;%s;%s;%d;%f;%f;%f;%f;%d;%s;%s' % (counter, region, store, order_id, total_oc_order, total_pos, sbr_total,
                                           check_total, control, date_of_check, auth_code))
    counter += 1
print('Сумма по чекам: ', check_result)
print('Сумма по банку: ', sbr_result)