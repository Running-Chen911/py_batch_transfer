from wicc.transactions import Transfer, TransferTransaction
from wicc.wallet import Wallet
from wallet_utils import WalletUtils
from wicc.cryptos import *

import sys

if __name__ == '__main__':

    fee_amount = 100000 #sawi
    key_file = "keys.txt"
    to_addr = "waQU7aFTVfJ5PoFuvVfWboKiWXBo45taKV"
    if len(sys.argv) == 3:
        key_file = sys.argv[1]
        to_addr = sys.argv[2]

    i = 0
    fo = open(key_file, "r", encoding='utf-8')
    for priv_key in fo.readlines():
        priv_key = priv_key.rstrip()
        i += 1
        # 实例化对象
        wu = WalletUtils(priv_key)
        print("")
        print("#", i, ": ", wu.get_addr(), " -> ", to_addr, sep='')

        # 获取账户余额
        # from_addr = wu.get_pubkey()
        free_amount = wu.get_token_free_amount("WUSD")
        if free_amount < fee_amount:
            print("free_amount:", free_amount, "insufficient error")
            continue

        to_amount = free_amount - fee_amount

        # 准备转账列表，并生成序列化待签名数据
        to_list = [
            Transfer(amount=to_amount, symbol="WUSD", to_addr=to_addr),
        ]

        tx = wu.get_tx_for_transfer("WUSD", fee_amount, "", to_list, "")

        # 生成raw_tx
        raw_tx = wu.gen_multisend_txraw(tx)
        # print(raw_tx)

        # 广播签名交易
        result = wu.submit_tx_raw(raw_tx)
        print(result)

    fo.close()
