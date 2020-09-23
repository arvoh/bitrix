import requests, json
import datetime
debug = False


def mark_to_tag(mark_code_raw):
    for i in ('(21)', '(01)'):
        mark_code_raw = mark_code_raw.replace(i, '')
    prefix = '0005'
    GTIN = int(mark_code_raw[0:14])
    GTIN_hex = str((hex(GTIN)).upper()[2:])
#    print('Length of GTIN', len(GTIN_hex))
    if len(GTIN_hex) <12:
        GTIN_hex = '0' * (12 - len(GTIN_hex)) + GTIN_hex
    GTIN_hex = prefix + GTIN_hex
    GTIN_hex = ' '.join(GTIN_hex[i:i + 2] for i in range(0, len(GTIN_hex), 2))
    mark_hex = ''
    mark = mark_code_raw[14:21]
    for i in mark:
        mark_hex = mark_hex + hex(ord(i))[2:]
    mark_hex = ' '.join(mark_hex[i:i + 2] for i in range(0, len(mark_hex), 2))
#    print(mark_hex)
    mark_to_send = GTIN_hex + ' ' + mark_hex
#    print('GTIN: ', GTIN)
#    print(GTIN_hex)
#    print('Mar to send: ', mark_to_send)
    return mark_to_send

def get_ofdURL(register_number, fn_number, doc_number, fpd):
    check_url = 'https://check.ofd.ru/rec/7111007621/%s/%s/%s/%s' % (register_number, fn_number, doc_number, fpd)
    return check_url

if debug:
    atol_url = 'https://testonline.atol.ru/possystem/v4/'
    group_code = 'v4-online-atol-ru_4179'
    INN = '5544332219'
    company = 'АТОЛ'
    payment_address = 'https://v4.online.atol.ru'
    login = 'v4-online-atol-ru'
    pawword = 'iGFFuihss'
else:
    atol_url = 'https://online.atol.ru/possystem/v4/'
    group_code = 'group_code_19683'
    INN = '7111007621'
    company = 'Федеральное государственное унитарное предприятие "Промсервис" Федеральной службы исполнения наказаний'
    payment_address = 'https://fsin-shop.ru/'
    login = '7ec24989-4388-43d8-bbf5-8cd91d9bdfd5'
    pawword = 'cbthVVrg'

def send_atol(extended_url, message):
    headers = {'Content-type': 'application/json;charset=utf-8'}
    return requests.post(atol_url + extended_url, message, headers=headers, verify=False)

def get_check_status(id):
    token = auth(login,pawword)
    extended_url = atol_url+'%s/report/%s?token=%s' %(group_code, id, token)
    a = json.loads(requests.get(extended_url).content)
    print(a)
    if a['error'] == None:
        print('Чек сформирован успешно')
        ecr_registration_number = a['payload']['ecr_registration_number']
        fpd = int(a['payload']['fiscal_document_attribute'])
        check_number = int(a['payload']['fiscal_document_number'])
        check_number_in_shift = int(a['payload']['fiscal_receipt_number'])
        fn_mumber = int(a['payload']['fn_number'])
        shift_number = int(a['payload']['shift_number'])
        check_date = a['payload']['receipt_datetime']
        total = float(a['payload']['total'])
        check_url = a['payload']['ofd_receipt_url']
        res = {
            'ecr_reg_number': ecr_registration_number,
            'fpd': fpd,
            'check_number': check_number,
            'check_number_in_shift': check_number_in_shift,
            'fn_mumber': fn_mumber,
            'shift_number': shift_number,
            'check_date': datetime.datetime.strptime(check_date, '%d.%m.%Y %H:%M:%S'),
            'total': total,
            'check_url': check_url
        }
        print('-'*80)
        print(res)
        return res






def auth(login, password):
    extended_url = 'getToken'
    req = {
         "login": login,
         "pass": password
        }
    req = json.dumps(req)
    a = send_atol(extended_url, req)
    a = a.json()
    try:
        return a['token']
    except:
        print('Ошибка при авторизации\n', a)

class Item:
    def __init__(self):
        self.name = ''
        self.price = float(0)
        self.quantity = float(0)
        self.sum = 0
        self.payment_method = "full_payment"
        self.payment_object = "commodity"
        self.vat = 'vat20'
        self.is_comissioner = False
        self.comission_address = ''
        self.comission_phone = ''
        self.comission_name = ''
        self.comission_inn = ''
        self.mark_row = ''

    def json(self):
        item = {
            'name': self.name,
            'price': self.price,
            'quantity': self.quantity,
            'sum': self.sum,
            'payment_method': self.payment_method,
            'payment_object': self.payment_object,
            'vat': {
                'type': self.vat
            }
        }
        if self.mark_row != '':
            item['nomenclature_code'] = mark_to_tag(self.mark_row)
        if self.is_comissioner:
            item['agent_info'] = {'type': 'commission_agent'}

            item['supplier_info'] = {'phones':(self.comission_phone,),
                                      'name': self.comission_name,
                                       'inn': self.comission_inn}
        return item




class Check:
    def __init__(self):
        self.token = auth(login,pawword)
        self._operation = 'sell'
        self.main_dict = {}
        self.clent_mail = ''
        self.order_number = 0
        self.extended_url = '%s/%s?token=%s' % (group_code, self._operation, self.token)
        self.organization_email = 'info@fguppromservis.ru'
        self.items = list()
        self.client_name = ''

    def set_operation(self, operation):
        if operation in ('sell', 'sell_refund'):
            self._operation = operation
        else:
            raise Exception('Не допустимый вид чека')

    def set_client_name(self, name):
        self.client_name = name

    def add_position(self, name, price, quantity, total, nds, is_comissioner = False, comission_name='',
                     comission_inn='', commission_phone='', mark_code=''):
        item = Item()
        item.name = name
        item.price = price
        item.mark_row = mark_code
        item.quantity = quantity
        item.sum = total
        item.vat = 'vat' + str(nds)
        item.is_comissioner = is_comissioner
        if is_comissioner == 1:
            # item.payment_object = "service" Убрано по договорённости с Жарковой С.Л.
            item.comission_name = str(comission_name).strip()
            item.comission_inn = comission_inn.strip()
            item.comission_phone = commission_phone
        self.items.append(item)

    def get_total(self):
        total = 0
        for i in self.items:
            total += i.sum
        return round(total, 2)

    def send_check(self):
        total = 0
        vat0 = 0
        vat10 = 0
        vat20 = 0

        if len(self.client_name) > 200:
            self.client_name = 'Не указано'

        self.main_dict['external_id'] = self.order_number + '**'
        recept = {}
        recept['client'] = {
            'email': self.clent_mail,
            'name': self.client_name
        }
        item_json = list()
        for item in self.items:
            item_json.append(item.json())
            total += item.sum
            if item.vat == 'vat0':
                vat0 += item.sum
            if item.vat == 'vat10':
                vat10 += item.sum
            if item.vat == 'vat20':
                vat20 += item.sum


        self.main_dict['receipt'] = recept
        company = {
            "email": self.organization_email,
            "sno": "osn",
            "inn": INN,
            "payment_address": payment_address
        }
        # self.main_dict['service'] = {'callback_url': 'google.ru'}
        self.main_dict['timestamp'] = datetime.datetime.now().strftime("%d.%M.%Y %H:%m:%S")
        recept['items'] = item_json
        self.main_dict['receipt']['company'] = company
        self.main_dict['receipt']['payments'] = [{
            'type': 1,
            'sum': total
        }]
        self.main_dict['receipt']['total'] = total
        if vat10 > 0 or vat20 > 0:
            self.main_dict['receipt']['vats'] = list()
#            if vat0 > 0:
#                self.main_dict['receipt']['vats'].append({'type':'vat0', 'sum' : 0})
            if vat10 > 0:
                self.main_dict['receipt']['vats'].append({'type': 'vat10', 'sum': round(vat10 / 11, 2)})
            #if vat20 > 0:
            self.main_dict['receipt']['vats'].append({'type': 'vat20', 'sum':round(vat20 / 6, 2)})
        print(json.dumps(self.main_dict))
        self.extended_url = '%s/%s?token=%s' % (group_code, self._operation, self.token)
        res = send_atol(self.extended_url, json.dumps(self.main_dict))
        print(res.json())
        if debug:
            print(json.dumps(self.main_dict))

        return res




# a = Check()
# a.order_number = '681455356864884'
# a.clent_mail = 'd.romanenko@fguppromservis.ru'
# item = Item()
# item.name = 'Детская кровать Micuna Sweet Bear'
# item.price = 111
# item.sum =  333
# item.quantity = 3
# item.vat = 'vat20'
# a.items.append(item)
#

# res = a.send_check()
get_check_status('467adba8-e466-4e52-aefb-2a4a6d2213dd')