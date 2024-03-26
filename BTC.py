from decimal import Decimal
from datetime import datetime
from OrderUtils import wallet_symbol
from OrderUtils import get_price as original_get_price
from OrderUtils import get_balance
from OrderUtils import buy_order
from OrderUtils import AddCrypto
from OrderUtils import GetCryptoFirstPrice
from OrderUtils import RemoveCrypto
from messageEvent import sendMessage
import time
import os
import asyncio
import tenacity

file_name = os.path.splitext(os.path.basename(__file__))[0]
crypto_name = file_name
symbol = f"{file_name}{wallet_symbol}"

BUY_THRESHOLD = 0.02  # = 2%
CHECK_INTERVAL = 2.5
MIN_BALANCE_FOR_BUY = 5.99

@tenacity.retry(stop=tenacity.stop_after_attempt(5), wait=tenacity.wait_fixed(2))
def get_price(symbol):
    return original_get_price(symbol)

@tenacity.retry(stop=tenacity.stop_after_attempt(5), wait=tenacity.wait_fixed(2))
def execute_buy_order(crypto_name):
    return buy_order(crypto_name)

if __name__ == "__main__":
    try:
        RemoveCrypto(crypto_name, GetCryptoFirstPrice(crypto_name))
        main_price = get_price(symbol)
        diff_price = main_price
        AddCrypto(crypto_name, main_price)
        while True:
            price = get_price(symbol)
            date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            print(f"{symbol}: {price:.5f}$ | {date} | Diff: {diff_price:.5f}")
            if price < (diff_price * (1 - BUY_THRESHOLD)):
                diff_price = price
                if get_balance(wallet_symbol) > MIN_BALANCE_FOR_BUY:
                    RemoveCrypto(crypto_name, GetCryptoFirstPrice(crypto_name))
                    execute_buy_order(crypto_name)
                    AddCrypto(crypto_name, main_price)
            time.sleep(CHECK_INTERVAL)
    except Exception as e:
        asyncio.run(sendMessage(f"{crypto_name} | Arrêt des vérifications en raison de l'erreur : {str(e)}"))
