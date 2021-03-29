import os
import base64
from hashlib import pbkdf2_hmac
from typing import Tuple

ITERATIONS = 100000


def get_salt() -> bytes:
    return os.urandom(32)


def make_hash(raw: str, salt: bytes) -> str:
    hash_ = pbkdf2_hmac('sha256', raw.encode('utf-8'), salt, ITERATIONS,
                        dklen=128)
    return serialize(hash_)


def serialize(b: bytes) -> str:
    return base64.b64encode(b).decode("ascii").strip()


def deserialize(s: str) -> bytes:
    return base64.b64decode(s.encode('ascii'))


def check_hash(raw: str, hash_: str, salt: str) -> bool:
    return make_hash(raw, deserialize(salt)) == hash_


def hash_password(raw_password: str) -> Tuple[str, str]:
    salt = get_salt()
    return make_hash(raw_password, salt), serialize(salt)
