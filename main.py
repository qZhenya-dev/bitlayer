from contracts.Bitlayer import Bitlayer
from models.accounts import Accounts
from models.coins import Coins

from utils.first_message import first_message
from core.client import Client
from utils.logs import logger
from core.modules import *
from config import *

import threading, time, random


def main():
    accounts_manager = Accounts()
    accounts_manager.loads_accs()
    accounts = accounts_manager.accounts

    bitlayer = Bitlayer(accounts[0])
    clients = [Client(account, Bitlayer(account)) for account in accounts]

    action = input("> 1. Запустить накрутку транзакций\n"
                   "> 2. Заклеймить награды за кол-во транзакций\n"
                   "> 3. Создать flash-ордера\n"
                   "> 4. Создать flash-ордер для конкретного адреса\n"
                   "> 5. Получить балансы BTC\n"
                   "> 6. Получить кол-во поинтов на аккаунтах\n"
                   "> ")
    print("-"*50+"\n")

    if action == "1":
        wrap_unwrap(clients)
    elif action == "2":
        claimer(clients)
    elif action == "3":
        create_orders(clients)
    elif action == "4":
        amount = int(input(f"> Введите объём для пополнения: "))
        address = input("> Введите адрес кошелька: ")

        for client in clients:
            if client.bitlayer.address.lower() == address.lower():
                create_order(client, amount)
    elif action == "5":
        balances_btc(clients)
    elif action == "6":
        balances_points(clients)
    else:
        logger.warning(f"Выбран вариант, которого нет!")


if __name__ == '__main__':
    first_message()
    main()


