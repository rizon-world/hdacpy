import os
import os.path
import subprocess
import shlex
import json
import re
import shutil
import time

import pexpect
import toml


from .errors import DeadDaemonException, FinishedWithError, InvalidContractRunType

def _process_executor(cmd: str, *args, need_output=False, need_json_res=True):
    res = None
    print(cmd.format(*args))
    child = pexpect.spawn(cmd.format(*args))    
    outs = child.read().decode('utf-8')

    if need_output == True:
        try:
            if need_json_res == True:
                res = json.loads(outs)
                print(res)
        except Exception as e:
            print(e)
            raise e


    return res


def _tx_executor(cmd: str, passphrase, *args):
    try:
        print(cmd.format(*args))
        child = pexpect.spawn(cmd.format(*args))
        outs_of_child = child.read_nonblocking(30000000, timeout=3)
        outs_of_child = child.sendline('Y')
        outs_of_child = child.read_nonblocking(10000, timeout=1)
        outs_of_child = child.sendline(passphrase)
        
        outs = child.read().decode('utf-8')
        print(outs)
        try:
            tx_hash = re.search(r'"txhash": "([A-Z0-9]+)"', outs).group(1)
            success = re.search(r'"success": (true|false)', outs).group(1)
        except Exception as e:
            print(outs_of_child)
            print(e)
            raise e

    except pexpect.TIMEOUT:
        raise FinishedWithError

    return tx_hash, success == 'true'


#################
## Daemon control
#################

def run_node(client_home: str = '.rizon') -> subprocess.Popen:
    """
    rizond start
    """
    client_home = os.path.join(os.environ["HOME"], client_home)
    proc = subprocess.Popen(shlex.split("rizond start --home {}".format(client_home)), stdout=subprocess.DEVNULL)
    return proc


def daemon_check(proc: subprocess.Popen):
    """
    Get proc object and check whether given daemon is running or not
    """
    if proc is None:
        return True
    else:
        is_alive = proc.poll() is None
        return is_alive



#################
## Setup CLI
#################

def init_chain(moniker: str, chain_id: str, client_home: str = '.rizon') -> subprocess.Popen:
    """
    rizond init <moniker> --chain-id <chain-id>
    """
    client_home = os.path.join(os.environ["HOME"], client_home)
    _ = _process_executor("rizond init {} --chain-id {} --home {}", moniker, chain_id, client_home)


def create_wallet(wallet_alias: str, client_home: str = '.rizon'):
    """
    rizond keys add my_key --keyring-backend test
    """
    client_home = os.path.join(os.environ["HOME"], client_home)
    cmd = "rizond keys add {} --home {} --keyring-backend test".format(wallet_alias, client_home)
    res = _process_executor(cmd, need_output=True, need_json_res=True)

    #address = None
    #pubkey = None
    #mnemonic = None

    #try:
    #    # If output keeps json form
    #    address = res['address']
    #    pubkey = res['pubkey']
    #    mnemonic = res['mnemonic']

    #except json.JSONDecodeError:
    #    try:
    #        # If output is not json
    #        address = re.search(r"address: ([a-z0-9]+)", outs).group(1)
    #        pubkey = re.search(r"pubkey: ([a-z0-9]+)", outs).group(1)
    #        mnemonic = outs.strip().split('\n')[-1]
    #    except Exception as e:
    #        print(res)
    #        raise e

    #except Exception as e:
    #    print(res)
    #    raise e

    #res = {
    #    "address": address,
    #    "pubkey": pubkey,
    #    "mnemonic": mnemonic
    #}

    print(res)
    return res


def get_wallet_info(wallet_alias: str, client_home: str = '.rizon'):
    """
    rizond keys show <wallet_alias>
    """
    client_home = os.path.join(os.environ["HOME"], client_home)
    res = _process_executor("rizond keys show {} --home {}", wallet_alias, client_home, need_output=True)
    return res


def delete_wallet(wallet_alias: str, client_home: str = '.rizon'):
    """
    rizond key delete <wallet_alias>
    """
    client_home = os.path.join(os.environ["HOME"], client_home)
    _ = _process_executor("rizond keys delete {} --home {}".format(wallet_alias, client_home))


def add_genesis_account(address: str, token: int, stake: str, client_home: str = '.rizon'):
    """
    Will deleted later

    rizond add-genesis-account <address> <initial_stake>
    """

    client_home = os.path.join(os.environ["HOME"], client_home)
    _ = _process_executor("rizond add-genesis-account {} {}uatolo,{}stake --home {}", address, token, stake, client_home)


def cli_configs(chain_id: str, client_home: str = '.rizon'):
    """
    rizond configs for easy use
    """
    client_home = os.path.join(os.environ["HOME"], client_home)
    cmds = [
        "rizond config chain-id {} --home {}".format(chain_id, client_home),
        "rizond config output json --home {}".format(client_home),
    ]

    for cmd in cmds:
        proc = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        outs, errs = proc.communicate()
        if proc.returncode != 0:
            print(errs)
            proc.kill()
            raise FinishedWithError


def enable_rest(client_home: str = '.rizon'):
    client_home = os.path.join(os.environ["HOME"], client_home)
    setting = toml.load('{}/config/app.toml'.format(client_home))
    setting['api']['enable'] = True

    f = open('{}/config/app.toml'.format(client_home), 'w')
    toml.dump(setting, f)
    f.close()


def gentx(wallet_alias: str, stake: int, chain_id: str, keyring_backend: str = 'test', client_home: str = '.rizon'):
    """
    rizond gentx <wallet_alias>
    """
    client_home = os.path.join(os.environ["HOME"], client_home)
    _ = _process_executor("rizond gentx {} {}stake --chain-id {} --keyring-backend {} --home {}", wallet_alias, stake, chain_id, keyring_backend,  client_home)


def collect_gentxs():
    """
    rizond collect-gentxs
    """
    _ = _process_executor("rizond collect-gentxs")

def validate_genesis():
    """
    rizond validate-genesis
    """
    _ = _process_executor("rizond validate-genesis")


def unsafe_reset_all():
    """
    rizond unsafe-reset-all
    """
    _ = _process_executor("rizond unsafe-reset-all")


def whole_cleanup():
    for item in [[".rizon", "config"], [".rizon", "data"], [".rizon"]]:
        path = os.path.join(os.environ["HOME"], *item)
        shutil.rmtree(path, ignore_errors=True)


def query_tx(tx_hash, client_home: str = ".rizon"):
    client_home = os.path.join(os.environ["HOME"], client_home)
    res = _process_executor("rizond query tx {} --home {}", tx_hash, client_home, need_output=True)
    return res

def tx_validation(res):
    is_success = res['logs'][0]['success']
    if is_success == False or "ERROR" in res['raw_log']:
        print(res['logs'])
    return res['logs'][0]['success'] and "ERROR" not in res['raw_log']

def query_contract(mode, address, path, client_home: str = ".rizon"):
    client_home = os.path.join(os.environ["HOME"], client_home)
    res = _process_executor("rizond contract query {} {} {} --home {}", mode, address, path, client_home, need_output=True)
    return res

def is_tx_ok(tx_hash):
    res = query_tx(tx_hash)
    return True if res['code'] == 0  else False


##################
## Rizon custom CLI
##################

def transfer_to(passphrase: str, recipient: str, amount: str, fee: str, from_value: str, node: str = "tcp://localhost:26657", client_home: str = '.rizon'):
    client_home = os.path.join(os.environ["HOME"], client_home)
    return _tx_executor("rizond hdac transfer-to {} {} {} --from {} --node {} --home {}", passphrase, recipient, amount, fee, from_value, node, client_home)

def get_balance(from_value: str, node: str = "tcp://localhost:26657", client_home: str = '.rizon'):
    client_home = os.path.join(os.environ["HOME"], client_home)
    res = _process_executor("rizond hdac getbalance --from {} --node {} --home {}", from_value, node, client_home, need_output=True)
    return res

def create_validator(passphrase: str, fee: str, from_value: str, pubkey: str, moniker: str, identity: str='""', website: str='""', details: str='""', node: str = "tcp://localhost:26657", client_home: str = '.rizon'):
    client_home = os.path.join(os.environ["HOME"], client_home)
    return _tx_executor("rizond hdac create-validator {} --from {} --pubkey {} --moniker {} --identity {} --website {} --details {} --node {} --home {}",
                      passphrase, fee, from_value, pubkey, moniker, identity, website, details, node, client_home)

