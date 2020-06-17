import bitrix

# Получим список закрытых заказов
sql = '''
select 
	*
from 
	oc_order_starta
where
	LAST_STATE = 1 and
    STATUS_ORDER = 3 and
    ORDER_ID > 122
    '''

bitrix.cursor.execute(sql)
res = bitrix.cursor.fetchall()
for i in res:
    print()
