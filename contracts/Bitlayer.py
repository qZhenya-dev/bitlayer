from contracts.default import Default
from utils.get_abi import get_abi
from utils.encode import get_data_byte64

from decimal import Decimal
from web3 import Web3
from eth_account.messages import encode_defunct


class Bitlayer(Default):
    def __init__(self, account):
        super().__init__(account.private_key, "https://rpc.bitlayer.org/", get_abi("wbtc"), "0xff204e2681a6fa0e2c3fade68a1b28fb90e4fc5f", account.proxy)

    def wrap(self, amount):
        transaction = self.contract.functions.deposit().build_transaction({
            'chainId': self.w3.eth.chain_id,
            'maxFeePerGas': int(self.w3.eth.gas_price * 1),
            'maxPriorityFeePerGas': int(self.w3.eth.gas_price * 1),
            'nonce': self.nonce(),
            'from': self.address,
            'value': self.gwei_to_wei(amount)
        })

        self.send_transaction(transaction, "wrap")

    def unwrap(self):
        transaction = self.contract.functions.withdraw(
            self.gwei_to_wei(self.token_balance(self.contract_address))
        ).build_transaction({
            'chainId': self.w3.eth.chain_id,
            'maxFeePerGas': int(self.w3.eth.gas_price * 1),
            'maxPriorityFeePerGas': int(self.w3.eth.gas_price * 1),
            'nonce': self.nonce(),
            'from': self.address,
            'value': hex(0)
        })

        self.send_transaction(transaction, "unwrap")

    def signature(self):
        message = "BITLAYER"
        signed_message = self.w3.eth.account.sign_message(encode_defunct(text=message), private_key=self.private_key)
        return signed_message.signature.hex()