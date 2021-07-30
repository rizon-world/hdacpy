import base64
import hashlib
import json
from typing import Any, Dict, List

import ecdsa
import requests

from rizonpy.exceptions import BadRequestException, EmptyMsgException, NotEnoughParametersException
from rizonpy.type import SyncMode
from rizonpy.wallet import privkey_to_address, privkey_to_pubkey, pubkey_to_address


class Transaction:
    """A Rizon transaction."""

    def __init__(
        self,
        *,
        host: str,
        privkey: str,
        memo: str = "",
        chain_id: str = "friday-devnet",
        gas_price: int = 100000000,
        sync_mode: SyncMode = 0,
    ) -> None:
        self._host = host
        self._privkey = privkey
        self._account_num = 0
        self._sequence = 0
        self._memo = memo
        self._chain_id = chain_id
        self._sync_mode = sync_mode
        self._gas_price = gas_price
        self._msgs: List[dict] = []

    def _get(self, url: str, params: dict) -> requests.Response:
        resp = requests.get(url, params=params)
        return resp

    def _post_json(self, url: str, json_param: dict) -> requests.Response:
        resp = requests.post(url, json=json_param)
        return resp

    def _put_json(self, url: str, json_param: dict) -> requests.Response:
        resp = requests.put(url, json=json_param)
        return resp

    def _get_account_info(self, address):
        url = "/".join([self._host, "cosmos/auth/v1beta1/accounts", address])
        res = self._get(url, None)
        if res.status_code != 200:
            raise BadRequestException

        resp = res.json()
        print(resp)
        # {
        #     'account': {
        #         '@type': '/cosmos.auth.v1beta1.BaseAccount',
        #         'address': 'rizon1h0k5l73xm7c7glhhkus9l448fc7slj463mw6rs', 
        #         'pub_key': {
        #             '@type': '/cosmos.crypto.secp256k1.PubKey', 
        #             'key': 'AkzT5j8E6uNV4IUHrxpxOX4qRgSOCjCq2lpNGzzF1ZWj'
        #         }, 
        #         'account_number': '0', 
        #         'sequence': '1'
        #     }
        # }
        self._account_num = int(resp["account"]["account_number"])
        self._sequence = int(resp["account"]["sequence"])

    def _get_pushable_tx(self) -> str:
        pubkey = privkey_to_pubkey(self._privkey)
        base64_pubkey = base64.b64encode(bytes.fromhex(pubkey)).decode("utf-8")
        pushable_tx = {
            "tx": {
                 "msg": self._msgs,
                 "fee": { "amount": [ { "amount": '500', "denom": 'uatolo' } ], "gas": '200000' },
                 "signatures": [
                   {
                     "account_number": str(self._account_num),
                     "sequence": str(self._sequence),
                     "signature": self._sign(),
                     "pub_key": {
                       "type": 'tendermint/PubKeySecp256k1',
                       "value": base64_pubkey
                     }
                   }
                 ],
                 "memo": self._memo
               },
               "mode": 'sync'
             }
        
        return pushable_tx

    def _sign(self) -> str:
        message_str = json.dumps(self._get_sign_message(), separators=(",", ":"), sort_keys=True)
        message_bytes = message_str.encode("utf-8")

        privkey = ecdsa.SigningKey.from_string(bytes.fromhex(self._privkey), curve=ecdsa.SECP256k1)
        signature_compact = privkey.sign_deterministic(
            message_bytes, hashfunc=hashlib.sha256, sigencode=ecdsa.util.sigencode_string_canonize
        )

        signature_base64_str = base64.b64encode(signature_compact).decode("utf-8")
        return signature_base64_str

    def _get_sign_message(self) -> Dict[str, Any]:
        return {
            "chain_id": self._chain_id,
            "account_number": str(self._account_num),
            "sequence": str(self._sequence),
            "fee":{ "amount": [ { "amount": '500', "denom": 'uatolo' } ], "gas": '200000' },
            "msgs": self._msgs,
            "memo": self._memo,
        }

    def _clear_msgs(self):
        self._msgs = []

    def _send_tx(self):
        tx = self._get_pushable_tx()
        #url = "/".join([self._host, "cosmos/tx/v1beta1/txs"])
        url = "/".join([self._host, "txs"])
        resp = self._post_json(url, json_param=tx)
        print(tx)
        print(resp.text)
        self._clear_msgs()

        if resp.status_code != 200:
            raise BadRequestException
        return resp.json()

    def batchSendTx(self):
        self._send_tx()


    ############################
    ## Transaction
    ############################

    ##############
    ## Query
    ##############

    def get_tx(self, tx_hash: str):
        url = "/".join([self._host, "txs", tx_hash])
        resp = self._get(url, None)
        if resp.status_code != 200:
            print(resp.text)
            raise BadRequestException

        return resp.json()


    # Looks like silly but possible in python
    def get_blocks(self, height: int = "latest"):
        url = "/".join([self._host, "blocks", height])
        resp = self._get(url, None)
        if resp.status_code != 200:
            print(resp.text)
            raise BadRequestException

        return resp.json()


    ############################
    ## Token
    ############################

    ## Tx

    def transfer(
        self,
        recipient_address: str,
        amount: int,
        memo: str = "",
        batch_mode: bool = False,
    ):
        sender_pubkey = privkey_to_pubkey(self._privkey)
        sender_address = pubkey_to_address(sender_pubkey)

        self._memo = memo
        self._get_account_info(sender_address)

        params = {
            "messages": [
                #{
                #    "@type": "/cosmos.bank.v1beta1.MsgSend",
                #    "from_address": sender_address,
                #    "to_address": recipient_address,
                #    "amount": [
                #        {
                #            "amount": str(amount),
                #            "denom": "uatolo"
                #        }
                #    ],
                #}
                {
                    "type": 'cosmos-sdk/MsgSend',
                    "value": {
                      "amount": [ { "amount": str(amount), "denom": 'uatolo' } ],
                      "from_address": sender_address,
                      "to_address": recipient_address
                    }
                }
            ],
        }

        msgs = params.get("messages")
        
        self._msgs.extend(msgs)

        if batch_mode == False:
            # 1 tx 1 msg
            return self._send_tx()
        # else:
            # just extend msgs and send via batchSendTx later

    ## Query

    def get_balance(self, address: str, blockHash: str = None):
        url = "/".join([self._host, "cosmos/bank/v1beta1/balances", address])
        #print(blockHash, type(blockHash))
        #if blockHash != None and blockHash != "":
        #    params["block"] = blockHash

        resp = self._get(url, None)
        if resp.status_code != 200:
            print(resp.text)
            raise BadRequestException

        return resp.json()

