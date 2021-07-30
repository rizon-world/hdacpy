import json
import pytest
from unittest.mock import Mock

from rizonpy.transaction import Transaction


def test_sign():
    private_key = "2afc5a66b30e7521d553ec8e6f7244f906df97477248c30c103d7b3f2c671fef"
    unordered_sign_message = {
        "chain_id": "friday-devtest",
        "account_number": "1",
        "fee": {"gas": "21906", "amount": [{"amount": "0", "denom": ""}]},
        "memo": "",
        "sequence": "0",
        "msgs": [
            {
                "type": "cosmos-sdk/Send",
                "value": {
                    "inputs": [
                        {
                            "address": "rizon18hpkjfem5j0htm2gh4zjfvdahraskp2jk9klan",
                            "coins": [{"amount": "1", "denom": "STAKE"}],
                        }
                    ],
                    "outputs": [
                        {
                            "address": "rizon1akujfn8qh9c7ayu0j40m2adnqf0nxutk3fq8kj",
                            "coins": [{"amount": "1", "denom": "STAKE"}],
                        }
                    ],
                },
            }
        ],
    }

    tx = Transaction(
        host="http://localhost:1317",
        privkey=private_key,
        chain_id="friday-devtest",
    )
    tx._get_sign_message = Mock(return_value=unordered_sign_message)  # type: ignore

    expected_signature = (
        "q9+/6SEM+p5JrWr1I0RREfbZ6fxKdgZUSBBXcD64WMYE+8uh91ql8aWIHAI9WEN/d3+uOkmW8GPfQp2KES2jIQ=="
    )

    actual_signature = tx._sign()
    assert actual_signature == expected_signature
