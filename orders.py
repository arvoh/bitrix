from colorama import Fore, Back, Style, init
import bitrix
from datetime import date
from time import sleep

def print_red(*args):
    print(Fore.RED, *args, Style.RESET_ALL)
def print_yellow(*args):
    print(Fore.YELLOW, *args, Style.RESET_ALL)
def log(message):
    f = open('closed_%s.log' % date.isoformat(), 'a', encoding='utf-8')

init()
while True:
    try:
        sql = '''
        select 
    order_id 
    from
    u0752174_delfin_exchange.oc_order_starta
    where
    LAST_STATE = 1 and
    STATUS_ORDER = 3 and
    order_id > 110 and
    order_id not in
    (
        select order_id from u0752174_delfin_exchange.Checks
    )
        '''

        bitrix.cursor.execute(sql)
        orders = bitrix.cursor.fetchall()
    except:
        print(Fore.RED + 'Не верно указан номер заказа' + Style.RESET_ALL)
    for i in orders:
        order_number = i[0]
        if order_number == 0:
            exit()
        try:
            order_details = bitrix.Order(order_number)
            log(order_number)
        except Exception as e:
            print_red(e)

        print('%-20s%s' %('Заказ №',order_details.order_id))
        print('%-20s%s' % ('Статус', order_details.bitrix_status))
        print('%-20s%s' % ('Клиент', order_details.FIO))
        print('%-20s%s' % ('E-mail', order_details.email))
        print('%-20s%s' % ('Регион', order_details.region))
        print('%-20s%s' % ('Магазин', order_details.store))
        print('=' * 40, 'Товар ' + '=' * 40)
        counter = 1

        print('%-4s%-70s%-10s%-10s%-10s' % ('№', 'Позиция', 'Кол-во', 'Цена', 'Сумма'))
        position_total = 0
        for i in order_details.items:
            print('%-4d%-70s%-10.2f%-10.2f%-10.2f%-5s' % (counter, i.name, i.quantity, i.price, i.total, str(i.is_change)))
            counter +=1
            position_total += i.total
        print('=' * 40, ' Оплаты ' + '=' * 40)
        payment_state = order_details.payment.staus
        if payment_state == 'Выполнено':
            color = Fore.GREEN
        if payment_state == 'Холдирование':
            color = Fore.YELLOW
        if payment_state == 'Отмена':
            color = Fore.RED
        if payment_state == 'Возврат':
            color = Fore.CYAN
        print('%-20s%s' % ( 'Статус', color + order_details.payment.staus + Style.RESET_ALL))
        print('%-20s%s' % ('Холдирование', order_details.payment.holded_sum))
        print('%-20s%s' % ('Завершение', order_details.payment.finish_sum))
        print('%-20s%s' % ('Разница', order_details.payment.holded_sum - order_details.payment.finish_sum))
        print('=' * 40, ' Чеки ' + '=' * 40)
        sql = 'select type,total, url from u0752174_delfin_exchange.Checks where order_id = %d' % order_details.order_id
        try:
            bitrix.cursor.execute(sql)
            checks = bitrix.cursor.fetchall()
        except Exception as e:
            print('Не удалось получить информацию по чекам')
            print(e)
        check_count = 0
        check_total = 0
        for i in checks:
            try:
                print('%-10s%-10.2f%s' % (i[0], i[1], i[2]))
                check_count +=1
                check_total = i[1]
            except:
                pass
        print('=' * 40, ' Проверки ' + '=' * 40)
        delta = order_details.payment.finish_sum - order_details.total
        print('%-20s%s' % ('Сумма oc_orders', order_details.total))
        print('%-20s%s' % ('Сумма по строкам', position_total))
        print('%-20s%s' % ('Сумма по банку', order_details.payment.finish_sum))
        if check_count == 1:
            print('%-20s%s' % ('Сумма по чеку', check_total))
        print('%-20s%s' % ('Переплата', delta))

        if delta > 0:
  #          if input('Провести возврат на сумму %.2f?: ' % delta) == 'Y':
            import rbs
            res = rbs.refund_order(order_details.sber_id, delta)
            order_details.good = True
            print(res.content)
        if check_count == 0:
            if (order_details.total == position_total and position_total == order_details.payment.finish_sum) or order_details.good:
                order_details.send_atol()
            else:
                sql = 'update `u0752174_delfin_exchange`.oc_order_starta set error = 1 where ORDER_ID = %d' % order_details.order_id
                try:
                    bitrix.cursor.execute(sql)
                    bitrix.connection.commit()
                except Exception as e:
                    print('Не удалось выполнить операцию\n', e)
        order_details = None
        sleep(30)
