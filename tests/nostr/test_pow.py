from pyrelay.nostr.event import NostrEvent
from pyrelay.nostr.pow import validate_pow


def test_validate_pow__valid():
    data = {
        "id": "000006d8c378af1779d2feebc7603a125d99eca0ccf1085959b307f64e5dd358",
        "pubkey": "a48380f4cfcc1ad5378294fcac36439770f9c878dd880ffa94bb74ea54a6f243",
        "created_at": 1651794653,
        "kind": 1,
        "tags": [
            [
                "nonce",
                "776797",
                "20"
            ]
        ],
        "content": "It's just me mining my own business",
        "sig": "284622fc0a3f4f1303455d5175f7ba962a3300d136085b9566801bc2e0699de0c7e31e44c81fb40ad9049173742e904713c3594a1da0fc5d2382a25c11aba977"
    }

    event = NostrEvent.deserialize(event=data)
    assert validate_pow(event)


def test_validate_pow__invalid():
    data = {
        'pubkey': '10ec2ceff21ab17f016e4e28f3509ec6bfdeb80f26997f281358f430e8bca754',
        'created_at': 1673416853,
        'kind': 1,
        'tags': [
            [
                'nonce',
                '776797',
                '20'
            ]
        ],
        'content': "It's just me mining my own business",
        'id': 'df86a2fb9eed09659246ea904404c7a15a6d99a205fa254f53748984fd25dbab',
        'sig': '8b5ce8345b96579a6763ffd62cc95034afd3b33d7263b6d3ec814d0aada2367a1c5b96d7983264e41b65cdac02ba2b98df619f5d02ec779aaf2cab7bd19d265c'
    }

    event = NostrEvent.deserialize(event=data)
    assert not validate_pow(event)
