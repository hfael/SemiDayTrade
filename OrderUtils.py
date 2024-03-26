from decimal import Decimal
from datetime import datetime
from messageEvent import sendMessage
import requests
import json
import time
import hmac
import hashlib
import urllib.parse
import os
import asyncio

API_KEY = 'enter api binance key here'
SECRET_KEY = 'enter secret binance key here'
BASE_URL = 'https://api.binance.com/api/v3'
folderName = os.path.dirname(os.path.abspath(__file__))

wallet_symbol = 'USDT'

jsonBuyedName = "buyed_crypto.json"
jsonCryptoListName = "crypto_list.json"
dirBuyedName = os.path.join(folderName, jsonBuyedName)
dirCryptoListName = os.path.join(folderName, jsonCryptoListName)


#=====================

def SaveData(filename, data):
    with open(filename, "w") as file:
        json.dump(data, file)

#=====================

def getCryptoList():
    try:
        with open(dirCryptoListName, "r") as file:
            data = json.load(file)
            if not data:
                data = []
    except FileNotFoundError:
        data = []
    except json.JSONDecodeError:
        data = []
    return data

def AddCrypto(item, price):
    data = getCryptoList()
    if item not in data:
        data.append({"name": item, "price": price})
        SaveData(dirCryptoListName, data)

def RemoveCrypto(item, price):
    data = getCryptoList()
    if item in data:
        data.remove({"name": item, "price": price})
        SaveData(dirCryptoListName, data)

def GetCryptoFirstPrice(item):
    data = getCryptoList()
    for entry in data:
        if entry["name"] == item:
            price = entry["price"]
            return price
            break

#=====================

def getBuyedList():
    try:
        with open(dirBuyedName, "r") as file:
            data = json.load(file)
            if not data:
                data = []
    except FileNotFoundError:
        data = []
    return data

def AddBuyedCrypto(item):
    data = getBuyedList()
    if item not in data:
        data.append(item)
        SaveData(dirBuyedName, data)

def RemoveBuyedCrypto(item):
    data = getBuyedList()
    if item in data:
        data.remove(item)
        SaveData(dirBuyedName, data)

#=====================


def generate_signature(data):
    return hmac.new(bytes(SECRET_KEY, 'utf-8'), bytes(data, 'utf-8'), hashlib.sha256).hexdigest()

def get_balance(symbol):
    timestamp = int(time.time() * 1000)
    data = f'timestamp={timestamp}'
    signature = generate_signature(data)
    account_info_url = f'{BASE_URL}/account?{data}&signature={signature}'
    headers = {'X-MBX-APIKEY': API_KEY}
    response = requests.get(account_info_url, headers=headers)
    if response.status_code == 200:
        account_data = json.loads(response.text)
        balance = next((float(asset['free']) for asset in account_data['balances'] if asset['asset'] == symbol), 0)
        if balance == 0:
            return 0
        return balance
    else:
        print(f"ERREUR données du compte: {response.text}")
        return 0

def get_price(symbol):
    url = f'{BASE_URL}/ticker/price?symbol={symbol}'
    response = requests.get(url)
    if response.status_code == 200:
        return float(response.json().get('price', 0))
    else:
        print(f"ERREUR récupération du prix: {response.text}")
        return 0


def get_symbol_filters(symbol):
    url = f"https://api.binance.com/api/v3/exchangeInfo"
    response = requests.get(url)
    if response.status_code == 200:
        exchange_info = response.json()
        return next((sym for sym in exchange_info['symbols'] if sym['symbol'] == symbol), None)
    else:
        return None


def buy_order(name):
    symbol = f"{name}{wallet_symbol}"
    timestamp = int(time.time() * 1000)
    symbol_info = get_symbol_filters(symbol)
    if symbol_info:
        step_size = float([filter['stepSize'] for filter in symbol_info['filters'] if filter['filterType'] == 'LOT_SIZE'][0])
        
    quantity = 6 / get_price(symbol)
    quantity = Decimal(quantity)
    quantity = round(float(quantity) / step_size) * step_size
    min_qty = float([filter['minQty'] for filter in symbol_info['filters'] if filter['filterType'] == 'LOT_SIZE'][0])

    quantity = round(quantity, 5)

    quantity = str(quantity)

    buy_order_params = {
        "symbol": symbol,
        "side": "BUY",
        "type": "MARKET",
        "quantity": quantity,
        "timestamp": timestamp,
        "recvWindow": 60000
    }

    query_string = urllib.parse.urlencode(buy_order_params, True)
    if 'timestamp' not in query_string:
        query_string += f"&timestamp={timestamp}"

    signature = generate_signature(query_string)
    query_string += f"&signature={signature}"


    url = "https://api.binance.com/api/v3/order"

    headers = {
        'X-MBX-APIKEY': API_KEY,
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    buy_order_params['signature'] = signature

    try:
        response = requests.post(url, headers=headers, data=buy_order_params)
        if response.status_code == 200:
            price = get_price(symbol)
            asyncio.run(sendMessage(f"{name} | Ordre d'achat placé avec succès (Prix d'achat: {price}$)"))
            AddBuyedCrypto(name)
            return response.json()
        else:
            respJson = response.json()
            asyncio.run(sendMessage(f"{name} | Erreur de d'achat: {respJson} | Q: {quantity}"))
            return None

    except Exception as e:
        return None

def sell_order(name):
    symbol = f"{name}{wallet_symbol}"
    timestamp = int(time.time() * 1000)
    symbol_info = get_symbol_filters(symbol)
    if symbol_info:
        step_size = float([filter['stepSize'] for filter in symbol_info['filters'] if filter['filterType'] == 'LOT_SIZE'][0])
        
    balance = get_balance(name)
    balance = float(balance)

    quantity = int(balance / step_size) * step_size


    if quantity <= 0:
        return None
    
    quantity = round(quantity, 5)

    quantity = str(quantity)

    sell_order_params = {
        "symbol": symbol,
        "side": "SELL",
        "type": "MARKET",
        "quantity": quantity,
        "timestamp": timestamp,
        "recvWindow": 60000
    }

    query_string = urllib.parse.urlencode(sell_order_params, True)
    if 'timestamp' not in query_string:
        query_string += f"&timestamp={timestamp}"

    signature = generate_signature(query_string)
    query_string += f"&signature={signature}"

    url = "https://api.binance.com/api/v3/order"

    headers = {
        'X-MBX-APIKEY': API_KEY,
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    sell_order_params['signature'] = signature

    try:
        response = requests.post(url, headers=headers, data=sell_order_params)
        if response.status_code == 200:
            RemoveBuyedCrypto(name)
            return response.json()
        else:
            respJson = response.json()
            asyncio.run(sendMessage(f"{name} | Erreur de vente: {respJson} | Q: {quantity}"))
            print(response.text)
            return None
    except Exception as e:
        return None

def get_symbol(name):
    return f"{name}{wallet_symbol}"
