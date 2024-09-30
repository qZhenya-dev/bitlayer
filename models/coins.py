from web3 import Web3
from utils.get_abi import get_abi

class CoinInfo:
    def __init__(self, coin, address, abi):
        w3 = Web3()

        self.coin = coin
        self.address = w3.to_checksum_address(address)
        self.abi = abi

class Coins:
    WBTC = CoinInfo(coin="WBTC", address="0xff204e2681a6fa0e2c3fade68a1b28fb90e4fc5f", abi=get_abi("wbtc"))
