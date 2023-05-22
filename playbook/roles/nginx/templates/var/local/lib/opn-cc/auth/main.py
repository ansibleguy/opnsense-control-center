#!/usr/bin/env python3

# {{ ansible_managed }}
# ansibleguy: opnsense-control-center
# flask application that acts as authentication service

from flask import Flask, request, render_template, redirect, Response
from waitress import serve

from config import PORT, AUTH_TYPE, LOCATION, ORIGIN_HEADER, MAIL_DOMAIN, \
    SESSION_LIFETIME, COOKIE_SESSION, COOKIE_USER
from session import has_valid_session, remove_expired_sessions, create_session
from util import debug
from type_ldap import auth_ldap
from type_file import auth_file
from type_system import auth_system
from type_totp import auth_totp

app = Flask('OPN-CC-Auth')

AUTH_MAPPING = {
    'system': auth_system,
    'file': auth_file,
    'ldap': auth_ldap,
    'totp': auth_totp,
}


def _authenticate(user: str, secret: str) -> bool:
    auth = AUTH_MAPPING[AUTH_TYPE](user=user, secret=secret)

    if auth:
        print(f"INFO: User '{user}' authentication successful.")

    else:
        print(f"WARNING: User '{user}' authentication failed.")

    return auth


def _redirect_origin() -> Response:
    origin = '/' if ORIGIN_HEADER not in request.headers else request.headers[ORIGIN_HEADER]
    return redirect(f"https://{request.headers['HOST']}{origin}")


@app.get(f"/{LOCATION}/login")
def form():
    debug(loc=f"{LOCATION}/login", msg=f"REQUEST | {request.__dict__}")

    if has_valid_session():
        response = _redirect_origin()
        debug(loc=f"{LOCATION}/login", msg=f"RESPONSE | {response.__dict__}")
        return response

    debug(loc=f"{LOCATION}/login", msg="RESPONSE | 200 - Rendering template")
    return render_template('login.html', LOCATION=LOCATION)


@app.post(f"/{LOCATION}/login")
def login():
    debug(loc=f"{LOCATION}/login", msg=f"REQUEST | {request.__dict__}")
    user, secret = request.form['u'], request.form['p']

    if _authenticate(user=user, secret=secret):
        response = _redirect_origin()
        token, session_time = create_session(user)
        response.set_cookie(
            key=COOKIE_SESSION,
            value=token,
            expires=session_time + SESSION_LIFETIME,
        )
        response.set_cookie(
            key=COOKIE_USER,
            value=user,
        )
        debug(loc=f"{LOCATION}/login", msg=f"RESPONSE | {response.__dict__}")
        return response

    debug(loc=f"{LOCATION}/login", msg='RESPONSE | 401')
    return 'unauthorized', 401


@app.get(f"/{LOCATION}")
def auth_request():
    debug(loc=LOCATION, msg=f'REQUEST | {request.__dict__}')
    if has_valid_session():
        response = Response()
        response.status_code = 200
        user = request.cookies[COOKIE_USER]
        mail_domain = MAIL_DOMAIN if MAIL_DOMAIN != '' else request.headers['HOST']
        response.headers['X_AUTH_REQUEST_USER'] = user
        response.headers['X_AUTH_REQUEST_EMAIL'] = f"{user}@{mail_domain}"
        debug(loc=LOCATION, msg=f"RESPONSE | {response.__dict__}")
        return response

    debug(loc=LOCATION, msg='RESPONSE | 401')
    return 'unauthorized', 401


@app.post(f"/{LOCATION}/cleanup")
def cleanup():
    debug(loc=f"{LOCATION}/cleanup", msg=f'REQUEST | {request.__dict__}')
    print('INFO: Starting session cleanup')
    remove_expired_sessions()
    print('INFO: Finished session cleanup')
    debug(loc=f"{LOCATION}/cleanup", msg='RESPONSE | 200')
    return 'done', 200


@app.route('/<path:path>')
def catch_all(path):
    debug(loc=path, msg=f'REQUEST | {request.__dict__}')
    response = redirect(f"https://{request.headers['HOST']}")
    debug(loc=path, msg='RESPONSE | 200')
    return response


if __name__ == '__main__':
    serve(app, host='127.0.0.1', port=PORT)
