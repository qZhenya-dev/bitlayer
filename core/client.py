from config import *
from utils.file_manager import append_to_txt
from utils.logs import logger
from utils.session import create_session

import time, random


class Client:
    def __init__(self, account, bitlayer):
        self.account = account
        self.bitlayer = bitlayer
        self.acc_name = bitlayer.acc_name

        self.session = create_session(self.account.proxy)

    def sleep(self, delay):
        s = random.randint(*delay)
        logger.info(f"{self.acc_name} ожидаем {s} сек..")
        time.sleep(s)

    def call(self, method, url, retJson=True, **params):
        try:
            resp = self.session.request(method.upper(), url, timeout=10, **params)
            return resp.json() if retJson else resp
        except Exception as e:
            logger.error(f"{self.acc_name} {e}")

    def login(self):
        resp = self.call("POST", "https://www.bitlayer.org/me/login", json={
            "address": self.bitlayer.address,
            "signature": f"0x{self.bitlayer.signature()}"
        })

        user = self.user()
        if not user or user["address"].lower() != self.bitlayer.address.lower():
            raise Exception(f"{self.bitlayer.address} ошибка при авторизации")

        return user

    def user(self):
        return self.call("GET", "https://www.bitlayer.org/me?_data=routes%2F%28%24lang%29._app%2B%2Fme%2B%2F_index")

    def start_task(self, taskId):
        return self.call("POST", "https://www.bitlayer.org/me/task/start", json={"taskId": int(taskId)})

    def verify_task(self, taskId):
        return self.call("POST", "https://www.bitlayer.org/me/task/verify", retJson=False, json={"taskId": int(taskId)})

    def claim_task(self, taskId, taskType):
        return self.call("POST", "https://www.bitlayer.org/me/task/claim", json={"taskId": int(taskId), "taskType": int(taskType)})

    def create_flash_order(self, amount=10):
        request_id = self.call("GET", "https://www.bitlayer.org/flash-bridge?_data=routes%2F%28%24lang%29._app%2B%2Fflash-bridge%2B%2F_index")["requestId"]
        order = self.call("POST", "https://www.bitlayer.org/flash-bridge/order?_data=routes%2F%28%24lang%29._app%2B%2Fflash-bridge%2B%2Forder", retJson=False, data={
            "amount": amount,
            "from_coin": "USDT",
            "to_coin": "BTC",
            "language": "en",
            "source": "",
            "address": self.bitlayer.address,
            "request_id": request_id
        })

        if order.status_code == 204:
            return {"request_id": request_id, "orderId": order.headers["X-Remix-Redirect"].split("/")[-1]}

    def get_order_info(self, orderId):
        self.call("GET", f"https://www.bitlayer.org/flash-bridge/orders/{orderId}?_data=root")
        self.call("GET", f"https://www.bitlayer.org/flash-bridge/orders/{orderId}?_data=routes%2F%28%24lang%29._app%2B%2Fflash-bridge%2B%2Forders")
        return self.call("GET", f"https://www.bitlayer.org/flash-bridge/orders/{orderId}?_data=routes%2F%28%24lang%29._app%2B%2Fflash-bridge%2B%2Forders.%24id")

