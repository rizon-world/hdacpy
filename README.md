# rizonpy

Tools for Hdac wallet management and offline transaction signing  
Forked from hukkinj1/cosmospy

<!--- Don't edit the version line below manually. Let bump2version do it for you. -->
> Version 0.5.6
> Tools for Hdac wallet management and offline transaction signing

## Version matching

| [Rizon](https://github.com/rizon-world/rizon) | `rizon` |
|------|----------|
| <= 0.9.0 | 0.5.0 |
| <= 0.4.0 | 0.3.3 |
| 0.5.0 | 0.4.0 |

## Installing

Installing from [Rizon PyPI repository](https://pypi.org/project/rizonpy):

```bash
pip install rizonpy
```

## Usage

### Prerequisite

Run node & rest-server in following step

* [Installation](https://docs.rizon.world/getting-started/install-rizon-platform)
* [Node start](https://docs.rizon.world/getting-started/deploy-own-network)
* [JSON RPC server start](https://docs.rizon.world/resource/cli/general)

This library runs on RESTful API

### Generating a wallet

```python
from rizonpy.wallet import generate_wallet
wallet = generate_wallet()
```

The value assigned to `wallet` will be a dictionary just like:

```python
{
    'private_key': '367360433d797cabd35361abdb3f6d0b94d27d7222d3af22a49028b7f4beb85d',
    'public_key': '0320a9b30c5fbbba3ffc34a1732c69365bc2a7de143f970318f8f1a2a38018dc6a',
    'address': 'rizon1jg8n39n2m93aavjnxl7snnvt4q6n50g9alxgkl',
    'mnemonic': 'often day image remove film awful art satisfy stable honey provide cactus example flock vacuum adult cool install erase able pencil cancel retreat win'
}
 ```

### Signing transactions

```python
from rizonpy.transaction import Transaction
tx = Transaction(
        host="http://localhost:1317",
        privkey="26d167d549a4b2b66f766b0d3f2bdbe1cd92708818c338ff453abde316a2bd59",
        chain_id="rizon-devtest",
    )
tx.transfer(
        token_contract_address="rizon1lgharzgds89lpshr7q8kcmd2esnxkfpwmfgk32",
        sender_address="rizon1lgharzgds89lpshr7q8kcmd2esnxkfpwmfgk32",
        recipient_address="rizon1z47ev5u5ujmc7kwv49tut7raesg55tjyk2wvhd",
        amount=amount, gas_price=2000000, fee=10000
    )
```

`transfer()` executes `POST` to organize tx, and `send_tx()` signs & broadcast the tx.
