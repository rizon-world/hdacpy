import bip32utils
from mnemonic import Mnemonic


def derive_root(seed: str) -> bip32utils.BIP32Key:
    return bip32utils.BIP32Key.fromEntropy(bytes.fromhex(seed))


def derive_child(
    root: bip32utils.BIP32Key, account: int = 0, index: int = 0
) -> bip32utils.BIP32Key:
    return (
        root.ChildKey(44 + bip32utils.BIP32_HARDEN)
        .ChildKey(1217 + bip32utils.BIP32_HARDEN)
        .ChildKey(account + bip32utils.BIP32_HARDEN)
        .ChildKey(0)
        .ChildKey(index)
    )


def mnemonic_to_key(mnemonic, account=0, index=0):
    seed = Mnemonic("english").to_seed(mnemonic).hex()
    root = derive_root(seed)
    child = derive_child(root, account, index)

    privkey = child.PrivateKey().hex()
    pubkey = child.PublicKey().hex()

    return privkey, pubkey
