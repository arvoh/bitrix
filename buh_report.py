import bitrix

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
    ORDER_ID > 122
    '''

bitrix.cursor.execute(sql)
res = bitrix.cursor.fetchall()
for i in res:
    order_id = i[0]
    total_oc_order = i[1]
    a = bitrix.Order(order_id)
    print('Сверка заказа № %d' % order_id)
    print()
    print(i)
