import bitrix
import atol
import json
from time import sleep

vats = {1: 20,
        2: 10,
        5: 0}

def load_tvl(order_id: int) -> atol.Check:
    try:
        order_id = int(order_id)
        file_name = 'TVL\\' + str(order_id) + '.txt'
        try:
            f = open(file_name, 'r', encoding='utf-8')
            json_sting=''
            for i in f:
                json_sting += i

            json_check = json.loads(json_sting)
            print(json_check)
        except Exception as error:
            print('При открытии файла произошла проблема\n', error)

        check = atol.Check()
        check.order_number = order_id
        check.clent_mail = json_check['1008']
        check.client_name = json_check['1227']
        for i in json_check['1059']:
            name = i['1030']
            price = i['1079'] / 100
            quantity = i['1023']
            total  = i['1043'] / 100
            nds = vats[i['1199']]
            #is_comissioner = True if i['1222'] == 32 else False
            is_comissioner = True if '1222' in i else False
            if is_comissioner:
                comissioner_phone = i['1224']['1171']
                comissioner_name = i['1224']['1225']
                comissioner_inn = i['1226']
                check.add_position(name,price,quantity,total,nds,is_comissioner,comissioner_name,comissioner_inn,comissioner_phone)
            else:
                check.add_position(name,price,quantity,total,nds)
        return check
    except Exception as e:
        print(e)

while True:
    a,b = None, None
    order_num = int(input('Заказ № '))
    b = bitrix.Order(order_num)
    a = load_tvl(order_num)
    delta = round(a.get_total() - b.total,2)
    print('Исходная сумма: ', b.total)
    print('Сумма по чеку:', a.get_total())
    print('Дельта:',  delta)
    print('Количество строк в исходном заказе: ', len(b.items))
    for i in range(len(b.items)):
        a.items.remove(a.items[0])
    print('Сумма по чеку после удаления:', a.get_total())
    if delta == a.get_total():
        if input('Пробить? ') == 'Y':
            a.set_operation('sell_refund')
            a.order_number = str(a.order_number) + '-Delta'
            res = a.send_check()
            res = res.json()['uuid']
            sleep(25)
            atol.get_check_status(res)
