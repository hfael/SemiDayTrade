from OrderUtils import get_price
from OrderUtils import get_symbol
from OrderUtils import get_balance
from OrderUtils import wallet_symbol
from OrderUtils import buy_order
from OrderUtils import sell_order
from OrderUtils import getBuyedList
from OrderUtils import getCryptoList
from OrderUtils import GetCryptoFirstPrice
from messageEvent import sendMessage
import datetime
import os
import time
import json
import asyncio

CHECK_INTERVAL = 1

if __name__ == "__main__":
    
    start_wallet = 0
    for name in getBuyedList():
        sSymbol = get_symbol(name)
        sPrice = get_price(sSymbol)
        sBalance = get_balance(name)
        start_wallet += sPrice * sBalance
    start_wallet += get_balance(wallet_symbol)
    asyncio.run(sendMessage(f"[SDT] Solde de départ: {start_wallet:.2f}$" ))
    secureVerif = False

    while True:
        date = datetime.datetime.now()
        print(len(getCryptoList()))
        if 0 <= date.hour < 24 and date.minute == 0  and 0 < date.second < 2:
            buyedList = getBuyedList()
            if secureVerif == False:
                secureVerif = True

                final_solde = 0
                for name in buyedList:
                    sSymbol = get_symbol(name)
                    sPrice = get_price(sSymbol)
                    sBalance = get_balance(name)
                    final_solde += sPrice * sBalance
                final_solde += get_balance(wallet_symbol)
                asyncio.run(sendMessage(f"[SDT] Solde du portefeuille: {final_solde:.2f}$" ))
                new_final_wallet = final_solde

                if date.hour == 23 or date.hour == 5 or date.hour == 11 or date.hour == 17:
                    cryptoAmount = len(buyedList)
                    asyncio.run(sendMessage(f"[SDT] Revente de {cryptoAmount} cryptomonnaie(s) !"))
                    for name in buyedList:
                        base_price = GetCryptoFirstPrice(name)
                        actual_price = get_price(get_symbol(name))
                        if actual_price > base_price * 1.03:
                            sell_order(name)
                            asyncio.run(sendMessage(f"[SDT] Vente rentable pour {name} (Prix de vente: {actual_price}$)"))
                        else:
                            asyncio.run(sendMessage(f"[SDT] Vente pas rentable pour {name} (Prix actuel: {actual_price}$)"))
                    time.sleep(1)
                    new_final_wallet = 0
                    for name in getBuyedList():
                        sSymbol = get_symbol(name)
                        sPrice = get_price(sSymbol)
                        sBalance = get_balance(name)
                        new_final_wallet += sPrice * sBalance
                    new_final_wallet += get_balance(wallet_symbol)
                    benefice = new_final_wallet - start_wallet
                    asyncio.run(sendMessage(f"[SDT] Bénéfice: {benefice:.2f}$" ))
                    start_wallet = new_final_wallet

        time.sleep(CHECK_INTERVAL)
        secureVerif = False
