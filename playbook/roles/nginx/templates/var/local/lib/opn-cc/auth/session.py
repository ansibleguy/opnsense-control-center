# {{ ansible_managed }}
# ansibleguy: opnsense-control-center

from time import time
from hashlib import sha512

import sqlite3
from flask import request

from config import SALT, SESSION_DB, SESSION_DB_TABLE, SESSION_LIFETIME, COOKIE_SESSION, COOKIE_USER
from util import debug


class SessionDB(object):
    def __init__(self):
        self.connection = sqlite3.connect(SESSION_DB)
        self.connection.row_factory = sqlite3.Row

    def __enter__(self) -> sqlite3.Connection:
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()


class SessionCursor(object):
    def __init__(self, session_db: sqlite3.Connection):
        self.cursor = session_db.cursor()

    def __enter__(self) -> sqlite3.Cursor:
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()


def _get_sessions(session_db: sqlite3.Connection) -> list:
    with SessionCursor(session_db) as session_db_cursor:
        return session_db_cursor.execute(
            f'SELECT user,token FROM {SESSION_DB_TABLE} WHERE time < {time() - SESSION_LIFETIME} ORDER BY id DESC'
        ).fetchall()


def _save_session(session_db: sqlite3.Connection, session_time: float, user: str, token: str):
    with SessionCursor(session_db) as session_db_cursor:
        session_db_cursor.execute(
            f"INSERT INTO {SESSION_DB_TABLE} (time,user,token) VALUES ('{session_time}','{user}','{token}')"
        )
    session_db.commit()


def create_session(user: str, password: str) -> tuple[str, float]:
    session_time = time()
    token = sha512(
        user.encode('utf-8') + password.encode('utf-8') + SALT
    ).hexdigest()
    with SessionDB() as session_db:
        _save_session(
            session_db=session_db,
            session_time=session_time,
            user=user,
            token=token,
        )

    return token, session_time


def _valid_session(session_db: sqlite3.Connection, user: str, token: str) -> bool:
    sessions = _get_sessions(session_db)
    debug(loc='?', msg=f'Session count: {len(sessions)}')

    if len(sessions) > 1000:
        print('WARNING: Many sessions in store!')

    for s in sessions:
        db_s_user, db_s_token = s[0], s[1]
        if db_s_user == user:
            if token == db_s_token:
                return True

            print(f"INFO: Invalid session token for user '{user}'!")
            break

    return False


def has_valid_session() -> bool:
    with SessionDB() as session_db:
        try:
            user = request.cookies[COOKIE_USER]
            token = request.cookies[COOKIE_SESSION]

            if _valid_session(session_db=session_db, user=user, token=token):
                return True

        except KeyError:
            pass

    return False


def remove_expired_sessions():
    with SessionDB() as session_db:
        with SessionCursor(session_db) as session_db_cursor:
            session_db_cursor.execute(
                f'DELETE FROM {SESSION_DB_TABLE} WHERE time < {time() - SESSION_LIFETIME}'
            )
