# {{ ansible_managed }}
# ansibleguy: opnsense-control-center

from time import time
from random import choice as random_choice
from string import ascii_letters, digits

from flask import request

from config import SESSION_LIFETIME, COOKIE_SESSION, COOKIE_USER
from crypto import encrypt, decrypt
from util import debug

TOKEN_SEPARATOR = ','


def create_session_token(user: str) -> tuple[str, float]:
    session_time = time()
    user = user.replace(TOKEN_SEPARATOR, '')
    token = encrypt(
        ''.join([random_choice(ascii_letters + digits) for _ in range(50)]) + TOKEN_SEPARATOR +
        user + TOKEN_SEPARATOR +
        f'{session_time}'
    )
    return token, session_time


def has_valid_session() -> bool:
    try:
        user = request.cookies[COOKIE_USER].replace(TOKEN_SEPARATOR, '')
        token = request.cookies[COOKIE_SESSION]
        token_cleartext = decrypt(token)
        debug(f"Cleartext session token: '{token_cleartext}'")

        if token_cleartext is not None:
            _, token_user, token_session_time = token_cleartext.split(TOKEN_SEPARATOR)
            lifetime_valid = (float(token_session_time) + SESSION_LIFETIME) > time()
            debug(
                f"Session token: user matches - {user == token_user} | "
                f"lifetime valid - {token_user}"
            )
            if user == token_user and lifetime_valid:
                return True

    except (KeyError, ValueError):
        pass

    return False
