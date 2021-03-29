from random import choice
from string import ascii_letters, digits

from social_network.db.models import AuthUser
from social_network.utils.security import check_hash


def is_valid_password(user: AuthUser, password: str) -> bool:
    user_password = user.password.get_secret_value()
    salt = user.salt.get_secret_value()
    return check_hash(password, user_password, salt)


def generate_token_value(length=255) -> str:
    alphabet = ascii_letters + digits
    return ''.join((choice(alphabet) for _ in range(length)))
