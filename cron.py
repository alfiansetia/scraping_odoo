import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import time
import json
base_path = os.getcwd()
# print(base_path)
path_session = os.path.join(base_path, 'session.json')
path_length = os.path.join(base_path, 'length.json')

dotenv_path = os.path.join(base_path, '.env')

load_dotenv(dotenv_path)
email = os.getenv("email")
passw = os.getenv("pass_odoo")
db_odoo = os.getenv("DB_ODOO")
base_url_odoo = os.getenv("BASE_URL_ODOO")
tele_group_id = os.getenv("TELE_GROUP_ID")
tele_bot_token = os.getenv("TELE_BOT_TOKEN")
fonte_token = os.getenv("FONTE_TOKEN")
group_wa = os.getenv("GROUP_WA")
url_backend_file = os.getenv("URL_BACKEND_FILE")
time_reload = 5
send_wa = True
current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

param = {
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "model": "stock.picking",
        "domain": [["picking_type_id", "=", 2]],
        "fields": ["name", "x_studio_no_do_manual", "date", "scheduled_date", "force_date", "partner_id", "location_dest_id", "location_id", "origin", "x_studio_tags", "x_studio_field_0rSR5", "priority_so", "note_to_wh", "note_itr", "invoice_state", "group_id", "backorder_id", "state", "priority", "picking_type_id", "sale_id"],
        "limit": 80,
        "sort": "",
        "context": {
            "lang": "en_US",
            "tz": "GMT",
            "uid": 192,
            "active_model": "stock.picking.type",
            "active_id": 2,
            "active_ids": [2],
            "search_default_picking_type_id": [2],
            "default_picking_type_id": 2,
            "contact_display": "partner_address",
            "search_default_available": 1,
            "search_disable_custom_filters": True
        }
    },
    "id": 613867950
}

def send_wa_message(message):
    res = requests.post('https://api.fonnte.com/send', headers={'Authorization': fonte_token}, json={'target': group_wa, 'message': message})
    res.raise_for_status()
    return res

def send_telegram_message(message):
    url = 'https://api.telegram.org/bot' + str(tele_bot_token) + '/sendMessage'
    payload = {'chat_id': tele_group_id, 'text': message}
    res = requests.post(url, data=payload)
    res.raise_for_status()
    return res

def read_session_from_file():
    try:
        with open(path_session, 'r') as file:
            data = json.load(file)
            return data.get('session', 0)
    except IOError:
        session = login_to_odoo()
        write_session_to_file(session)
        return session

def write_session_to_file(session):
    with open(path_session, 'w') as file:
        json.dump({'session': session}, file)

def login_to_odoo():
    with requests.Session() as sesi:
        url_login_page = base_url_odoo + '/web?db=' + str(db_odoo)
        response = sesi.get(url_login_page)
        soup = BeautifulSoup(response.content, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'}).get('value')
        url_login = base_url_odoo + '/web/login'
        login_data = {'csrf_token': csrf_token, 'db': db_odoo, 'login': email, 'password': passw}
        try:
            login_response = sesi.post(url_login, data=login_data)
            session_id = login_response.cookies.get('session_id')
            return session_id
        except:
            return ''

def read_length_from_file():
    try:
        with open(path_length, 'r') as file:
            data = json.load(file)
            return data.get('length', 0)
    except IOError:
        return 0

def write_length_to_file(length):
    with open(path_length, 'w') as file:
        json.dump({'length': length}, file)

def get_headers():
    session_id = read_session_from_file()
    headers = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/json',
        'x-requested-with': 'XMLHttpRequest',
        'Cookie': "session_id=" + str(session_id)
    }
    return headers

        
def get_file_so(id_so):
    try :
        headers = get_headers()
        url_print_so = base_url_odoo + '/web/dataset/call_button'
        param_print_So = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "args": [
                    [
                        id_so
                    ],
                    {
                        "lang": "en_US",
                        "tz": "GMT",
                        "uid": 192,
                        "params": {
                            "id": 12508,
                            "action": 338,
                            "model": "sale.order",
                            "view_type": "form",
                            "menu_id": 211
                        },
                        "search_default_my_quotation": 1
                    }
                ],
                "method": "print_so",
                "model": "sale.order"
            },
            "id": 425211742
        }
        response_file = requests.post(url=url_print_so, headers=headers, json=param_print_So)
        url_file = str(response_file.json()['result']['url'])
        return base_url_odoo+url_file
    except:
        return ''

def main():
    selisih = 0
    length = read_length_from_file()
    headers = get_headers()
    response = requests.post(base_url_odoo + '/web/dataset/search_read', headers=headers, json=param)
    if response.status_code != 200:
        ses = login_to_odoo()
        write_session_to_file(ses)
        # raise Exception('Error from odoo code : ' + str(response.status_code))
    response.raise_for_status()
    try:
        result = response.json()
    except:
        raise Exception('Error Response from odoo!')
    new_length = result['result']['length']
    if length == 0:
        length = new_length
        write_length_to_file(length)
    if length < new_length and length > 0 and selisih <= 10:
        selisih = new_length - length
        length = new_length
        write_length_to_file(length)
        print('Jumlah berubah! kirim notif!')
        text = '===New ' + str(selisih) + ' DO!===\n\n'
        for i in range(selisih):
            url_file = url_backend_file + '/printso/' + str(result['result']['records'][i]['sale_id'][0])
            text += str(i+1) +". DO : " + str(result['result']['records'][i]['name'])
            text += "\nSO : " + str(result['result']['records'][i]['group_id'][1])
            text += "\nTO : " + str(result['result']['records'][i]['partner_id'][1])
            text += "\nFILE : " + url_file
            if selisih <= 3:
                text += "\nNote : " + str(result['result']['records'][i]['note_to_wh'])
            text += '\n'
        send_telegram_message(text)
        if(send_wa):
            send_wa_message(text)
    if selisih >= 10:
        t = 'New '+ str(length) +' DO!, More Than 10! '
        send_telegram_message(t)
        if(send_wa):
            send_wa_message(t)
    print(current_time + ' => Jumlah Data : ' + str(length))

if __name__ == "__main__":
    main_length = read_length_from_file()
    try:
        main()
    except Exception as e:
        write_length_to_file(main_length)
        ter = "Error: " + str(e)
        print(ter)
        send_telegram_message('===Program Error!===\n'+ ter)