

from time import sleep
from atol import Check, Item, get_check_status
# atol.debug = True
# atol.set_test_maode()
# a = atol.Check()
# a.client_name = 'Tester'
# a.order_number = '17052917561851301127'
# a.add_position('колбаса Клинский Брауншвейгская с/к в/с', 1000, 0.3, 300, '10')
# a.clent_mail = 'kkt@kkt.ru'
# a.send_check()
import atol
#a = Check()
#a.order_number = '1-to_del-11'
#a.clent_mail = 'd.romanenko@fguppromservis.ru'
#item = Item()
#item.name = 'Детская кровать Micuna Sweet Bear'
#item.price = 111
#item.sum = 111
#item.quantity = 1
#item.vat = 'vat20'
#item.mark_row = '44 4D 00 00 02 C0 EE D8 58 3F 69 6F 2B 71 43 41 42 6D 38 20 20'
#a.set_operation('sell_refund')
#a.items.append(item)


#res = a.send_check()

#res = res.json()
#for i in res:
#    print(i,':', res[i])
#sleep(10)
#get_check_status(res['uuid'])

import bitrix
a = bitrix.Order(3713)
a.email = 'd.romanenko@fguppromservis.ru'
a.send_atol()
