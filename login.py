import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
base_path = os.getcwd()
# print(base_path)

dotenv_path = os.path.join(base_path, '.env')

load_dotenv(dotenv_path)
email = os.getenv("email")
passw = os.getenv("pass_odoo")
db_odoo = os.getenv("DB_ODOO")
base_url_odoo = os.getenv("BASE_URL_ODOO")
url_backend = os.getenv("URL_BACKEND_FILE")

def login_to_odoo():
    with requests.Session() as sesi:
        url_login_page = base_url_odoo + '/web?db='+ str(db_odoo)
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

if __name__ == "__main__":
    try:
        session_id = login_to_odoo()
        url = url_backend + str('/api/setting/env')
        res = requests.post(url=url, data={
            'env_value' : session_id
        })
        # print(res.text)
        print(session_id)
    except Exception as e:
        ter = "Error: " + str(e)
        print(ter)