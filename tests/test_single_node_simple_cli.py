import time
import json
import os

from rizonpy.transaction import Transaction as Tx
from rizonpy.wallet import mnemonic_to_privkey, mnemonic_to_address
from rizonpy.exceptions import BadRequestException

import pytest

from .lib import cmd
from .lib.errors import DeadDaemonException, DaemonNotProducingBlock

class TestSingleNode():
    proc_ee = None
    proc_friday = None
    proc_rest = None

    chain_id = "testchain"
    moniker = "testnode"

    wallet_elsa = "elsa"
    wallet_anna = "anna"
    wallet_olaf = "olaf"
    wallet_hans = "hans"

    info_elsa = None
    info_anna = None
    info_olaf = None
    info_hans = None

    basic_stake = "10000000000"
    basic_coin = "10000000000"
    basic_coin_amount = int(basic_coin)

    transfer_amount = 100000
    transfer_fee = 100000

    tx_block_time = 2


    def daemon_healthcheck(self):
        is_friday_alive = cmd.daemon_check(self.proc_friday)
        if not is_friday_alive:
            if not is_friday_alive:
                print("Friday dead")

            raise DeadDaemonException


    def daemon_downcheck(self):
        is_friday_alive = cmd.daemon_check(self.proc_friday)
        if is_friday_alive:
            for _ in range(10):
                print("Friday alive")
                self.proc_friday.kill()
                time.sleep(10)
                is_friday_alive = cmd.daemon_check(self.proc_friday)
                if not is_friday_alive:
                    break

            else:
                raise DeadDaemonException


    def setup_class(self):
        """
        Make genesis.json and keys
        """
        print("*********************Test class preparation*********************")

        print("Cleanup double check")
        cmd.whole_cleanup()

        print("Init chain")
        cmd.init_chain(self.moniker, self.chain_id)
        cmd.unsafe_reset_all()

        print("Apply general clif config")
        cmd.cli_configs(self.chain_id)
        cmd.enable_rest()

        print("Create wallet")
        self.info_elsa = cmd.create_wallet(self.wallet_elsa)
        self.info_anna = cmd.create_wallet(self.wallet_anna)
        #self.info_olaf = cmd.create_wallet(self.wallet_olaf, self.wallet_password)
        #self.info_hans = cmd.create_wallet(self.wallet_hans, self.wallet_password)

        print("Collect info and make transaction sender")
        self.tx_elsa = Tx(
            chain_id=self.chain_id,
            host="http://localhost:1317",
            privkey=mnemonic_to_privkey(self.info_elsa["mnemonic"])
        )

        self.tx_anna = Tx(
            chain_id=self.chain_id,
            host="http://localhost:1317",
            privkey=mnemonic_to_privkey(self.info_anna["mnemonic"])
        )

        print("Add genesis account in cosmos way")
        cmd.add_genesis_account(self.info_elsa['address'], self.basic_coin, self.basic_stake)
        cmd.add_genesis_account(self.info_anna['address'], self.basic_coin, self.basic_stake)
        #cmd.add_genesis_account(self.info_olaf['address'], self.basic_coin, self.basic_stake)
        #cmd.add_genesis_account(self.info_hans['address'], self.basic_coin, self.basic_stake)

        print("Gentx")
        cmd.gentx(self.wallet_elsa, self.basic_stake, self.chain_id)
        print("Collect gentxs")
        cmd.collect_gentxs()
        print("Validate genesis")
        cmd.validate_genesis()

        print("*********************Setup class done*********************")


    def teardown_class(self):
        """
        Delete all data and configs
        """
        print("Test finished and teardowning")
        cmd.delete_wallet(self.wallet_anna)
        cmd.delete_wallet(self.wallet_elsa)
        cmd.whole_cleanup()


    def setup_method(self):
        print("Running friday node..")
        self.proc_friday = cmd.run_node()

        # Waiting for nodef process is up and ready for receiving tx...
        time.sleep(10)
        cmd._process_executor("ps", "-al", need_output=True, need_json_res=False)


        self.daemon_healthcheck()
        print("Runup done. start testing")


    def teardown_method(self):
        print("Terminating daemons..")
        self.proc_friday.terminate()
        self.daemon_downcheck()

        print("Reset blocks")
        cmd.unsafe_reset_all()


    def test00_rest_get_balance(self):
        print("======================Start test00_rest_get_balance======================")
        
        res = self.tx_elsa.get_balance(self.info_elsa['address'])
        print("Output: ", res)
        # {'balances': [{'denom': 'stake', 'amount': '0'}, {'denom': 'urizon', 'amount': '10000000000'}], 'pagination': {'next_key': None, 'total': '2'}}
        amount = None
        for coin in res['balances']:
            if coin['denom'] == 'uatolo':
                amount = coin['amount']
                break
        assert(float(amount) / self.multiplier == self.basic_coin_amount) 

        res = self.tx_anna.get_balance(self.info_anna['address'])
        print("Output: ", res)
        for coin in res['balances']:
            if coin['denom'] == 'uatolo':
                amount = coin['amount']
                break
        assert(float(amount) / self.multiplier == self.basic_coin_amount) 

        print("======================Done test00_rest_get_balance======================")


    def test01_rest_transfer_to(self):
        print("======================Start test01_rest_transfer_to======================")

        print("Transfer token from elsa to anna")
        res = self.tx_elsa.transfer(self.info_anna['address'], self.transfer_amount)
        print(res)
        
        print("Tx sent. Waiting for validation")
        time.sleep(self.tx_block_time * 3 + 1)

        print("Check whether tx is ok or not")
        is_ok = cmd.is_tx_ok(res["txhash"])
        assert(is_ok == True)

        print("Balance checking after transfer..")
        res = self.tx_anna.get_balance(self.info_anna['address'])
        amount = None
        for coin in res['balances']:
            if coin['denom'] == 'uatolo':
                amount = coin['amount']
                break
        assert(int(amount) == self.basic_coin_amount + int(self.transfer_amount))

        res = self.tx_elsa.get_balance(self.info_elsa['address'])
        for coin in res['balances']:
            if coin['denom'] == 'uatolo':
                amount = coin['amount']
                break
        assert(int(amount) <  self.basic_coin_amount - int(self.transfer_amount))

        print("======================Done test01_rest_transfer_to======================")


