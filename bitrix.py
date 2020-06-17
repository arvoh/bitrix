from datetime import datetime
import pymysql
from _datetime import datetime
test = False
settings = {'host': '31.31.198.53',
            'database': 'u0752174_fsin_new',
            'user': 'u0752174_site_ex',
            'password': 'L7y7L1c6',
            'use_unicode': True}

try:
    connection = pymysql.connect(**settings)
except Exception as error:
    print('Не удалось подключиться к БД\nОтвет сервера: ', error)
cursor = connection.cursor()

def add_check_db(order_id, check_id, type = 'Приход', error = ''):
    sql = "insert into u0752174_delfin_exchange.Checks(order_id, check_id,type, error)" \
          "values(%d, '%s', '%s', '%s')" % (order_id, check_id, type, error)
    print(sql)
    cursor.execute(sql)
    connection.commit()


class Item:
    def __init__(self, name, price, quantity, total, NDS, is_change, is_comission=0, comission_phone='', comission_name='',  commission_inn=''):
        self.name = name
        self.price = float(price)
        self.quantity = quantity
        self.total = float(total)
        self.NDS = int(NDS)
        self.is_change = is_change
        self.is_comission = is_comission
        if self.is_comission == 1:
            self.comission_inn = commission_inn
            # self.comission_phone = list()
            self.comission_phone = comission_phone
            self.comission_name = comission_name


class Payment:
    def __init__(self, sber_id):
        import rbs
        payment_details = rbs.get_order_extended(sber_id)
        if payment_details['errorCode'] == '0':
            self.payment_status = 'ok'
            self.staus = rbs.order_status[payment_details['orderStatus']]
            self.date = datetime.fromtimestamp(payment_details['date'] / 1000)
            self.transaction = payment_details['authRefNum']
            self.holded_sum = float(payment_details['paymentAmountInfo']['approvedAmount'] / 100)
            self.finish_sum = float(payment_details['paymentAmountInfo']['depositedAmount'] / 100)
        else:
            self.payment_status = 'error'


class Recept:
    def __init__(self, type_of_check, fd_number, number_in_shift, shift_number, date_time, total):
        self.type = type_of_check
        self.fd_number = fd_number
        self.number_in_shift = number_in_shift
        self.shift_number = shift_number
        self.date = date_time
        self.total = total


class Order:
    def __init__(self, order_id):
        sql = 'SELECT ' \
              'order_id, FIO, FIO_RECIPIENT, RECIPIENT_BIRTH, DATE_ORDER, STATUS_ORDER, TEXT_CANCEL, TOTAL, ID_SHOP ' \
              'FROM u0752174_delfin_exchange.oc_order_starta ' \
              'where order_id = %d;' % order_id
        try:
            cursor.execute(sql)
            if cursor.rowcount == 0:
                raise Exception('Отсутствует информация о заказе')
            order_details = cursor.fetchone()
        except Exception as error:
            raise Exception('Нет информации о заказе: ' + str(error))

        # Маловероятная ситуация но сверим ID
        if order_id != order_details[0]:
            raise Exception('Не совпадает номер заказа')
        self.order_id = order_id
        self.FIO = order_details[1]
        self.FIO_recipient = order_details[2]
        self.recipient_birth = order_details[3]
        self.date_create = order_details[4]
        self.exchange_status = order_details[5]
        self.cancel_text = order_details[6]
        self.total = float(order_details[7])
        try:
            self.ID_SHOP = int(order_details[8])
            sql = 'select name, parent_id from u0752174_delfin_exchange.oc_store_category where category_id = %d' % self.ID_SHOP
            cursor.execute(sql)
            store = cursor.fetchone()
            self.store = store[0]
            self.ID_REGION = store[1]
            sql = 'select name from u0752174_delfin_exchange.oc_store_category where category_id = %d' % self.ID_REGION
            cursor.execute(sql)
            region = cursor.fetchone()
            self.region = region[0]
        except:
           self.ID_SHOP = 0
           self.store = ''
           self.ID_REGION = ''
           self.region = ''

        #Получение электронной почты
        sql = 'SELECT EMAIL FROM u0752174_fsin_new.b_user where id in (SELECT USER_ID FROM u0752174_fsin_new.b_sale_order where ID = %d);' % self.order_id
        cursor.execute(sql)
        self.email = cursor.fetchone()[0]
        # Запрос из битрикса состояния
        SQL = 'SELECT STATUS_ID FROM u0752174_fsin_new.b_sale_order where ID = %d' % self.order_id
        try:
            cursor.execute(SQL)
        except Exception as e:
            print('Ошибка при получении статуса из Битрикс\nОтвет сервера: ', e)
        bitrix_status = cursor.fetchone()[0]
        if bitrix_status == 'P':
            self.bitrix_status = 'В работе'
        if bitrix_status == 'F':
            self.bitrix_status = 'Выполнен'
        elif bitrix_status == 'OT':
            self.bitrix_status = 'Отменён'
        sql = 'SELECT value FROM u0752174_fsin_new.b_sale_order_props_value where ORDER_ID = %d and ORDER_PROPS_ID = 10;' % order_id
        try:
            cursor.execute(sql)
        except Exception as e:
            print('Ошибка при получении ID Сбербанка из Битрикс\nОтвет сервера: ', e)
        self.sber_id = cursor.fetchone()[0]

        self.payment = Payment(self.sber_id)

        #Информация о чеках
        self.checks = list()
        sql = 'SELECT type, check_id, fd_number, number_in_shift, shift_number, date_time, total ' \
              'FROM u0752174_delfin_exchange.Checks where order_id = %d' % self.order_id
        try:
            cursor.execute(sql)
        except Exception as e:
            raise Exception('Не удалось выполнить запрос\n%s\n%s' %(sql,e))
        check_from_db = cursor.fetchall()
        for i in check_from_db:
            check_dict = {
                'type_of_check': i[0],
                'fd_number': i[2],
                'number_in_shift': i[3],
                'shift_number': i[4],
                'date_time': i[5],
                'total': float(i[6])
            }
            self.checks.append(Recept(**check_dict))

        # Получение товаров из промежуточной БД
        sql = 'SELECT NAME,PRICE, QUANTITY, PRODUCT_SUM, NDS, ISCHANGE, commission, comissioner_phone,comissioner_name, comissioner_inn  ' \
              'FROM u0752174_delfin_exchange.oc_order_products_starta where quantity > 0 and order_id = %d' % self.order_id
#        print(sql)
        cursor.execute(sql)
        res = cursor.fetchall()
        self.items = []
        for product in res:
            if product[6] == 0 or product[6] == None:
                self.items.append(Item(product[0], product[1], product[2], product[3], product[4], product[5]))
            elif product[6] == 1:
                self.items.append(Item(product[0], product[1], product[2], product[3], product[4], product[5], product[6], product[7], product[8], product[9]))

    def send_atol(self, check_type='sell'):
        from atol import Check
        check = Check()
        check.set_operation(check_type)
        check.order_number = str(self.order_id) + '-' + check._operation
        if test:
            check.clent_mail = 'd.romanenko@fguppromservis.ru'
        else:
            check.clent_mail = self.email
        check.client_name = '%s (Заказ № %s)' % (self.FIO, self.order_id)

        for item in self.items:
            if item.total == 0 or item.quantity == 0:
                continue
            if not item.is_comission:
                check.add_position(item.name, item.price, item.quantity, item.total, item.NDS, item.is_comission)
            else:
                check.add_position(item.name, item.price, item.quantity, item.total, item.NDS, item.is_comission,item.comission_name, item.comission_inn, item.comission_phone)
        if check.get_total() == self.total:
            print('Сумма сошлась')
            res = check.send_check().json()
            print(res)
            check_id = res['uuid']
            if res['error'] != None:
                error_message = res['error']['text']
                add_check_db(self.order_id,check_id, 'Приход', error_message)
            else:
                add_check_db(self.order_id, check_id)
            from time import sleep
            sleep(15)
            from atol import get_check_status
            a = get_check_status(check_id)
            print(a)
            from atol import get_ofdURL
            url = get_ofdURL('0004524074004440', a['check_number'], a['fn_mumber'], a['fpd'])
            sql = 'update u0752174_delfin_exchange.Checks ' \
                  'set ecr_reg_number = "%s", fpd = %d,fd_number = %d,number_in_shift = %d, shift_number = %d, fn = %d, date_time = "%s", total = %f, url = "%s" ' \
                  'where check_id = "%s"' % (a['ecr_reg_number'], a['fpd'], a['check_number'], a['check_number_in_shift'], a['shift_number'], a['fn_mumber'], a['check_date'].isoformat(), a['total'], url, check_id)
            cursor.execute(sql)
            connection.commit()
            print(res['uuid'])
        else:
            print('не пошла сумма')




# while True:
#     order_number = int(input('Номер заказа: '))
#     if order_number == 0:
#         exit()
#
#     order = Order(order_number)
#     print('Сумма заказа: ', order.total)
#     print('Сумма по банку: ', order.payment.finish_sum)
#     sum_control = 'Совпадает' if order.total == order.payment.finish_sum else 'Не совпадает'
#     print('Результат проверки: ', sum_control)
#     if input('Сформировать чек') == '1':
#         order.send_atol()
#     #order.send_atol('sell')
# from atol import get_check_status
# # get_check_status('467adba8-e466-4e52-aefb-2a4a6d2213dd')
