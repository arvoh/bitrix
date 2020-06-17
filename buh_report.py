import bitrix

# Получим список закрытых заказов

a = bitrix.Order(207)
for i in a.checks:
    print(i.type,
          i.total)
