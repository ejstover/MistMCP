from __future__ import annotations

import json
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption
from jwt.utils import base64url_encode


def rsa_to_jwk(private_key: rsa.RSAPrivateKey, kid: str) -> dict:
    numbers = private_key.private_numbers()
    public_numbers = numbers.public_numbers
    jwk = {
        "kty": "RSA",
        "kid": kid,
        "use": "sig",
        "alg": "RS256",
        "n": base64url_encode(public_numbers.n.to_bytes((public_numbers.n.bit_length() + 7) // 8, "big")).decode(),
        "e": base64url_encode(public_numbers.e.to_bytes((public_numbers.e.bit_length() + 7) // 8, "big")).decode(),
        "d": base64url_encode(numbers.d.to_bytes((numbers.d.bit_length() + 7) // 8, "big")).decode(),
        "p": base64url_encode(numbers.p.to_bytes((numbers.p.bit_length() + 7) // 8, "big")).decode(),
        "q": base64url_encode(numbers.q.to_bytes((numbers.q.bit_length() + 7) // 8, "big")).decode(),
        "dp": base64url_encode(numbers.dmp1.to_bytes((numbers.dmp1.bit_length() + 7) // 8, "big")).decode(),
        "dq": base64url_encode(numbers.dmq1.to_bytes((numbers.dmq1.bit_length() + 7) // 8, "big")).decode(),
        "qi": base64url_encode(numbers.iqmp.to_bytes((numbers.iqmp.bit_length() + 7) // 8, "big")).decode(),
    }
    return jwk


def main() -> None:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    kid = "dev-key-1"
    jwk = rsa_to_jwk(key, kid)
    output = {"keys": [jwk]}
    Path("dev_jwks.json").write_text(json.dumps(output, indent=2))

    pem = key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption())
    Path("dev_private.pem").write_bytes(pem)


if __name__ == "__main__":
    main()
