import hashlib

import bech32
import ecdsa
from mnemonic import Mnemonic
from rizonpy.type import Wallet
import rizonpy.bip39_bip44_process as bip_to_mnemonic

PREFIX = "rizon"
KEYWORD_PUB = "pub"


def generate_wallet() -> Wallet:
    m = Mnemonic("english")
    mnemonic = m.generate(strength=256)

    privkey, pubkey = bip_to_mnemonic.mnemonic_to_key(mnemonic)
    address = pubkey_to_address(pubkey)
    return {"private_key": privkey, "public_key": pubkey, "address": address, "mnemonic": mnemonic}


def privkey_to_pubkey(privkey: str) -> str:
    privkey_obj = ecdsa.SigningKey.from_string(bytes.fromhex(privkey), curve=ecdsa.SECP256k1)
    pubkey_obj = privkey_obj.get_verifying_key()
    return pubkey_obj.to_string("compressed").hex()


def pubkey_to_address(pubkey: str) -> str:
    pubkey_bytes = bytes.fromhex(pubkey)
    c = hashlib.new('sha256')
    c.update(pubkey_bytes)
    sha256ed = c.digest()

    addressed = hashlib.new('ripemd160')
    addressed.update(sha256ed)
    r = addressed.digest()
    return bech32.bech32_encode(PREFIX, bech32.convertbits(r, 8, 5))


def privkey_to_address(privkey: str) -> str:
    pubkey = privkey_to_pubkey(privkey)
    return pubkey_to_address(pubkey)


def mnemonic_to_privkey(mnemonic):
    privkey, _ = bip_to_mnemonic.mnemonic_to_key(mnemonic)
    return privkey


def mnemonic_to_pubkey(mnemonic):
    _, pubkey = bip_to_mnemonic.mnemonic_to_key(mnemonic)
    return pubkey


def mnemonic_to_address(mnemonic):
    _, pubkey = bip_to_mnemonic.mnemonic_to_key(mnemonic)
    return pubkey_to_address(pubkey)
