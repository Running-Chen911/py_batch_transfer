from wicc-wallet-utils.transactions import Transfer, TransferTransaction
from wicc-wallet-utils.wallet import Wallet
from submitsendtx import TransferToken

import sys

class KeyInfo:
    def __init__(self, file):
        self.file = file

    def getPrivkeys(self):
        privkeys = set()
        f = open(self.file, "r", encoding='utf-8')
        for line in f.readlines():
            privkeys.add(line.strip())
        return privkeys


if __name__ == '__main__':

    key_file = sys.argv[1]
    to_addr = sys.argv[2]
    fee_amount = 100000

    keys = KeyInfo(key_file).getPrivkeys()
    for privkey in keys:
        # 实例化对象
        tt = TransferToken(privkey)
        # 获取账户余额
        from_addr = tt.get_pubkey_from_privkey()
        free_amount = tt.get_token_free_amount(from_addr, "WUSD")
        to_amount = free_amount - fee_amount

        # 准备转账列表，并生成序列化待签名数据
        to_list = [
            Transfer(amount=to_amount, symbol="WUSD", to_addr=to_addr),
        ]
        tx = tt.get_tx_for_transfer("WUSD", fee_amount, from_addr, to_list, "")

        # 生成raw_tx
        raw_tx = tt.gen_multisend_txraw(tx)
        print(raw_tx)

        # 广播签名交易
        result = tt.submit_tx_raw(raw_tx)
        print(result)
