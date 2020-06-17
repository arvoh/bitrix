import bitrix

while True:
    order_id = int(input('Номер заказа: '))
    if order_id == 0:
        exit()
    try:
        a = bitrix.Order(order_id)
    except Exception as e:
        print('Ошибка\n', e)
        continue
    print('Заказ № ',order_id)
    print('Сумма из ДиФ ', a.total)
    print('Сумма по завершения ', a.payment.finish_sum)
    print('Сумма по холдирования ', a.payment.finish_sum)
    print('Разблокировка у клиента ', a.payment.delta)
    print('Возврат по банку', a.payment.refunded_amount)
    print('Статус по банку ', a.payment.staus)
