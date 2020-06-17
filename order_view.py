import bitrix

while True:
    order_id = int(input('Номер заказа: '))
    if order_id == 0:
        exit()
    a = bitrix.Order(order_id)
    print('Заказ № ',order_id)
    print('Оплата ', a.total)
    print('Сумма по банку ', a.payment.finish_sum)
    print('Статус по банку ', a.payment.staus)
