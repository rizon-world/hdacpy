import rizonpy.wallet as address

test_vector = {
    'private_key': '700f97c741663c679b440b4c65d61a3119c46c45627a86b53f98c63faa8bfb24',
    'public_key': '0219b123d03301bcbf0537193b46e56874c87e594c595cdb93a0b4ddf171c54229',
    'address': 'rizon18hpkjfem5j0htm2gh4zjfvdahraskp2jk9klan',
    'mnemonic': 'often day image remove film awful art satisfy stable honey provide cactus example flock vacuum adult cool install erase able pencil cancel retreat win'
    }


def test_mnemonic_to_privkey():
    assert address.mnemonic_to_privkey(test_vector["mnemonic"]) == test_vector['private_key']


def test_mnemonic_to_pubkey():
    assert address.mnemonic_to_pubkey(test_vector["mnemonic"]) == test_vector['public_key']


def test_mnemonic_to_address():
    assert address.mnemonic_to_address(test_vector["mnemonic"]) == test_vector['address']


def test_privkey_to_pubkey():
    assert address.privkey_to_pubkey(test_vector["private_key"]) == test_vector["public_key"]


def test_privkey_to_address():
    assert address.privkey_to_address(test_vector["private_key"]) == test_vector["address"]


def test_generate_wallet(mocker):
    mock_urandom = mocker.patch("os.urandom")
    mock_urandom.return_value = b"\x1e\xd2\x7f9\xa7\x0em\xfd\xa0\xb4\xaa\xc4\x0b\x83\x0e%\xbf\xe6DG\x7f:a\xe6#qa\x1ch5D\xa9"  # noqa: E501
    expected_wallet = {
        'private_key': '0e94ebba9ade3ee6839ac29920ddb7e3ad074766caa825abe511c3021da2281b',
        'public_key': '03e98766ca52975cd441927d768910af324276545be5082bea2f917ed0c8fad3a8',
        'address': 'rizon1akujfn8qh9c7ayu0j40m2adnqf0nxutk3fq8kj',
        'mnemonic': 'burst negative solar evoke traffic yard lizard next series foster seminar enter wrist captain bulb trap giggle country sword season shoot boy bargain deal'
    }
    assert address.generate_wallet() == expected_wallet
