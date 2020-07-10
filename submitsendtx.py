"""
    环境: python3
    pip install wicc-wallet-utils==0.0.1
"""

from wicc-wallet-utils.transactions import Transfer, TransferTransaction
from wicc-wallet-utils.wallet import Wallet

import json
import requests

main_net_baas_url = "https://baas.wiccdev.org/v2/api"
test_net_baas_url = "https://baas-test.wiccdev.org/v2/api"


class TransferToken:
    def __init__(self, privkey, main_net=False):
        self.main_net = main_net
        self.privkey = privkey
        self.wallet = Wallet(privkey, main_net=self.main_net)

    def get_pubkey_from_privkey(self):
        public_key = self.wallet.chain_coin.privtopub(self.privkey)
        return public_key

    def get_addr_from_privkey(self):
        public_key = self.wallet.chain_coin.privtopub(self.privkey)
        address = self.wallet.chain_coin.pubtoaddr(public_key)
        return address

    def get_addr_from_pubkey(self, public_key):
        address = self.wallet.chain_coin.pubtoaddr(public_key)
        return address

    def get_regid(self, addr):
        data = self.get_accountinfo(addr)
        return data["regid"]

    def post_data_to_baas(self, uri, request):
        if self.main_net:
            url = main_net_baas_url + uri
        else:
            url = test_net_baas_url + uri
        header = {
            "Content-Type": "application/json",
            'Connection': 'close'
        }
        request = json.dumps(request)
        resp = requests.post(url=url, data=request, headers=header)
        return resp.json()

    def get_token_free_amount(self, addr, token_name="WICC"):
        uri = "/account/getaccountinfo"
        post_data = {"address": addr}
        response = self.post_data_to_baas(uri, post_data)
        print(response)
        tokens = response["data"]["tokens"]
        if token_name in tokens:
            return tokens[token_name]["freeAmount"]
        else:
            return 0

    def get_current_height(self):
        uri = "/block/getblockcount"
        post_data = {}
        response = self.post_data_to_baas(uri, post_data)
        return response["data"]

    def get_accountinfo(self, addr):
        uri = "/account/getaccountinfo"
        post_data = {"address": addr}
        response = self.post_data_to_baas(uri, post_data)
        return response["data"]

    def get_tx_for_transfer(self, symb, total_fees, addr, to_list, memo):
        tx_data = TransferTransaction()
        # 获取当前高度
        tx_data.valid_height = self.get_current_height()
        # 转账方regid
        if "-" in addr:
            tx_data.regid = addr
        else:
            tx_data.pubkey = addr

        # 矿工费类型
        tx_data.fee_coin_symbol = symb
        # 收款方列表
        tx_data.transfer_list = to_list
        # 矿工费大小
        tx_data.fee_amount = total_fees
        # memo
        tx_data.memo = memo

        return tx_data

    def gen_multisend_txraw(self, tx_data):
        rawtx = self.wallet.transfer_tx(tx_data)
        return rawtx

    def submit_tx_raw(self, raw_tx):
        uri = "/transaction/sendrawtx"
        post_data = {
            "rawtx": raw_tx
        }
        return self.post_data_to_baas(uri, post_data)


if __name__ == '__main__':
    # 实例化对象
    privkey = "Y9UwaHP1HGajDyeut8KdrYftFyTohTeS9YNo2uVtfrudYJjbLDWM"
    transfer_obj = TransferToken(privkey)

    # 获取账户余额
    addr = transfer_obj.get_addr_from_privkey()
    pubkey = transfer_obj.get_pubkey_from_privkey()
    print(addr, pubkey)
    wusd_free_amount = transfer_obj.get_token_free_amount(addr, "WICC")
    wicc_free_amount = transfer_obj.get_token_free_amount(addr, "WUSD")
    wgrt_free_amount = transfer_obj.get_token_free_amount(addr, "WGRT")
    print("wusd_free_amount: ", wusd_free_amount)
    print("wicc_free_amount: ", wicc_free_amount)
    print("wgrt_free_amount: ", wgrt_free_amount)

    # 准备转账列表，并生成序列化待签名数据
    to_list = [
        Transfer(amount=1 * 10 ** 8, symbol="WICC", desert_address="wYXV7QzHZnb8LuWw7Xa24dfUTqmH2tNZBq"),
        Transfer(amount=1 * 10 ** 8, symbol="WUSD", desert_address="wYXV7QzHZnb8LuWw7Xa24dfUTqmH2tNZBq"),
        Transfer(amount=1 * 10 ** 8, symbol="WGRT", desert_address="wYXV7QzHZnb8LuWw7Xa24dfUTqmH2tNZBq"),
    ]
    tx = transfer_obj.get_tx_for_transfer(addr, to_list)

    # 生成raw_tx
    raw_tx = transfer_obj.gen_multisend_txraw(tx)
    print(raw_tx)

    # 广播签名交易
    result = transfer_obj.submit_tx_raw(raw_tx)
    print(result)
