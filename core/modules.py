import threading, time
import random

from config import *
from utils.logs import logger

from decimal import Decimal


def create_order(client, amount):
    client.login()
    order = client.create_flash_order(amount)
    order_info = client.get_order_info(order["orderId"])

    if not send_only_address: logger.info(f"{client.acc_name} сумма для перевода: {order_info['amount']} USDT")

    for payment in order_info["payments"]:
        if not deposit_chain:
            logger.info(f"{client.acc_name} {payment['asset']} {payment['address']}")
        elif deposit_chain.upper() == payment["chain"]:
            print(payment["address"]) if send_only_address else logger.info(f"{client.acc_name} {payment['asset']} {payment['address']}")

def create_orders(clients):
    print("* Вы можете указать 5, тогда бот будет генерировать адреса 5ти аккаунтов по очереди, это нужно для того, чтобы вы успевали отправить средста на все аккаунты")
    count_one_time = int(input(f"> Введите кол-во кошельков для генерации адресов для депозита: "))
    print()

    amounts = [1000, 500, 100, 50, 20, 10, 5]
    print(f"* Доступые суммы для пополнения {amounts}")
    amount = int(input(f"> Введите объём для пополнения: "))
    if amount not in amounts:
        logger.warning(f"неподходящий объём {amount}")
        return
    print()

    ths = []
    for client in clients:
        try:
            if len(ths) == count_one_time:
                for th in ths: th.start()
                for th in ths: th.join()
                ths = []

                input(f"Нажмите enter для продолжения ")

            if client.bitlayer.balance() == 0 or not send_only_null_balance:
                ths.append(threading.Thread(target=create_order, args=(client, amount)))

        except Exception as e:
            logger.error(f"{client.acc_name} {e}")

    if len(ths) < count_one_time:
        for th in ths: th.start()
        for th in ths: th.join()

def balances_btc(clients):
    def balance(client):
        balance_btc = client.bitlayer.balance()
        logger.info(f"{client.acc_name} {0 if 0 == balance_btc else balance_btc} BTC")

    for client in clients:
        threading.Thread(target=balance, args=(client,)).start()

def balances_points(clients):
    def balance(client):
        client.login()
        balance_points = client.user()["profile"]["totalPoints"]
        logger.info(f"{client.acc_name} {0 if 0 == balance_points else balance_points} POINTS")

    for client in clients:
        threading.Thread(target=balance, args=(client,)).start()

def wrap_unwrap(clients):
    timeouts = {}
    thxs = {}
    state = {}

    while True:
        try:
            time.sleep(10)

            for i, client in enumerate(clients.copy()):
                acc_name = client.acc_name

                if acc_name not in timeouts:
                    user = client.login()
                    timeouts[acc_name] = time.time() + (random.randint(*delay_start) * i)
                    state[acc_name] = "wrap"

                    txs = random.randint(*count_txs) - int(user['profile']['txn'])
                    if txs < 0: txs = 0

                    thxs[acc_name] = {"max": txs, "count": 0}
                    logger.info(f"{acc_name} всего {user['profile']['txn']}, будет сделано {txs} транзакций")

                if thxs[acc_name]["max"] <= thxs[acc_name]["count"]:
                    clients.remove(client)
                    continue

                if time.time() >= timeouts[acc_name]:
                    if state[acc_name] == "wrap":
                        amount = round(client.bitlayer.balance() * Decimal(0.7), 9)
                        logger.info(f"{acc_name} будет врапнуто {amount} BTC")
                        client.bitlayer.wrap(amount)
                        state[acc_name] = "unwrap"

                    elif state[acc_name] == "unwrap":
                        logger.info(f"{acc_name} анврапаем BTC")
                        client.bitlayer.unwrap()
                        state[acc_name] = "wrap"

                    thxs[acc_name]["count"] += 1
                    delay = random.randint(*delay_actions)
                    logger.info(f"{acc_name} ожидаем {delay}с. перед {state[acc_name]}")

            if not clients:
                logger.success("все транзакции были сделаны")
                break

        except Exception as e:
            logger.error(f"{acc_name} {e}")

def claimer(clients):
    def claim(client):
        user = client.login()
        txn = int(user["profile"]["txn"])
        for task in user["tasks"]["advanceTasks"]:
            if task["logoType"] == "transaction" and task["taskType"] == 3:
                if not task["isCompleted"] and txn >= task["targetCount"]:
                    client.start_task(task["taskId"])
                    verify = client.verify_task(task["taskId"])

                    if verify.status_code == 200:
                        client.claim_task(task["taskId"], task["taskType"])
                        logger.info(f"{client.acc_name} заклеймили {task['title']} +{task['rewardPoints']}POINTS")

    for client in clients:
        threading.Thread(target=claim, args=(client,)).start()






