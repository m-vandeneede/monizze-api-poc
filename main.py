import hashlib, time, math, json, os
import requests
from constants import *
from dotenv import load_dotenv

def main():
    #Load environment
    load_dotenv()
    
    #Attempt to login
    login_token = get_login_token()
    
    #Fetch data
    user_details = get_user_details(login_token)
    meal_exp_details = get_product_expiry(login_token, 'emv')
    eco_exp_details = get_product_expiry(login_token, 'eco')
    covid_exp_details = get_product_expiry(login_token, 'ecv')
    
    #Pretty print
    print()
    print('-----------------------------------------------')
    print(f'Name:       {user_details["firstName"]} {user_details["lastName"]}')
    print(f'Email:      {user_details["email"]}')
    print()
    print(f'Bal. ECO:   {user_details["balanceEco"]}€ {pretty_print_expiry(eco_exp_details)}')
    print(f'Bal. COVID: {user_details["balanceEcv"]}€ {pretty_print_expiry(covid_exp_details)}')
    print(f'Bal. MEAL:  {user_details["balanceEmv"]}€ {pretty_print_expiry(meal_exp_details)}')
    print('-----------------------------------------------')

def pretty_print_expiry(exp_details):
    if exp_details:
        return f'({exp_details["amount"]}€ expiring on {exp_details["date"]})'
    else: return ''

def get_product_expiry(token, product):
    parms = {'product': product}
    response = requests.get(API_EXPIRY_URI, headers=build_x_monizze_headers(token), params=parms)
    
    if response.status_code == 200:
        expiry_data = json.loads(response.content)['expiry']
        if len(expiry_data) > 0:
            return expiry_data[0]
        else: return None
    else:
        raise Exception(f"Received status code {response.status_code} on productexpiry request.")

def get_user_details(token):
    response = requests.get(API_USERDETAIL_URI, headers=build_x_monizze_headers(token))
    
    if response.status_code == 200:
        return json.loads(response.content)['user']
    else:
        raise Exception(f"Received status code {response.status_code} on userdetail request.")

def get_login_token():
    user = os.getenv('USERNAME')
    pwd = os.getenv('PASSWORD')
    
    print(f'Logging in user: {user}')
    
    params = {'login': user, 'password': pwd}
    
    response = requests.post(API_LOGIN_URI, headers=build_x_monizze_headers(), params=params)
    
    if response.status_code == 200:
        login_token = json.loads(response.content)['token']
        print(f'Login succesful, received token: {login_token}')
        return login_token
    else:
        raise Exception(f"Received status code {response.status_code} on login request.")

def get_app_token(cur_epoch):
    app_secret = os.getenv('APP_SECRET')
    hash_source = f'{cur_epoch}{APP_VERSION}{app_secret}'
    return hashlib.md5(str.encode(hash_source)).hexdigest()

def build_x_monizze_headers(login_token=None):
    cur_epoch = math.floor(time.time())
    app_token = get_app_token(cur_epoch)
    print(f'Current epoch: {cur_epoch}; App token: {app_token}')
    
    headers = {'x-application': APP_PLATFORM, 'x-version': APP_VERSION, 'x-monizze-app-token': app_token, 'x-time': str(cur_epoch)}
    
    if login_token:
        headers['x-monizze-login-token'] = login_token
    
    return headers
    

if __name__ == "__main__":
    main()