#!/usr/bin/env python3

# {{ ansible_managed }}
# ansibleguy: opnsense-control-center
# flask application that acts as authentication service

from flask import Flask, request, render_template, redirect, Response
from waitress import serve

from config import PORT, AUTH_USER_TYPE, AUTH_TOKEN_TYPE, LOCATION, ORIGIN_HEADER, MAIL_DOMAIN, \
    FORM_PARAM_USER, FORM_PARAM_PWD, FORM_PARAM_TOKEN, \
    SESSION_LIFETIME, COOKIE_SESSION, COOKIE_USER
from session import has_valid_session, create_session_token
from util import debug
from type_ldap import auth_ldap
from type_pam import auth_system, auth_totp
from type_multi import auth_multi

app = Flask('OPN-CC-Auth')

AUTH_MAPPING = {
    'ldap': auth_ldap,
    'system': auth_system,
    'totp': auth_totp,
}


def _authenticate(user: str, secret_user: str, secret_token: (str, None)) -> bool:
    if secret_token is None:
        auth = AUTH_MAPPING[AUTH_USER_TYPE](user=user, secret=secret_user)

    else:
        auth = auth_multi(
            user=user, secret_user=secret_user, secret_token=secret_token,
            user_auth=AUTH_USER_TYPE, token_auth=AUTH_TOKEN_TYPE,
        )

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
    return render_template(
        'login.html',
        LOCATION=LOCATION,
        FORM_PARAM_PWD=FORM_PARAM_PWD, FORM_PARAM_USER=FORM_PARAM_USER, FORM_PARAM_TOKEN=FORM_PARAM_TOKEN
    )


@app.post(f"/{LOCATION}/login")
def login():
    debug(loc=f"{LOCATION}/login", msg=f"REQUEST | {request.__dict__}")
    user = request.form[FORM_PARAM_USER]
    secret_user = request.form[FORM_PARAM_PWD]
    secret_token = request.form[FORM_PARAM_TOKEN] if FORM_PARAM_TOKEN in request.form else None

    if _authenticate(
            user=user,
            secret_user=secret_user,
            secret_token=secret_token
    ):
        response = _redirect_origin()
        token, session_time = create_session_token(user)
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


@app.route('/<path:path>')
def catch_all(path):
    debug(loc=path, msg=f'REQUEST | {request.__dict__}')
    response = redirect(f"https://{request.headers['HOST']}")
    debug(loc=path, msg='RESPONSE | 200')
    return response


if __name__ == '__main__':
    serve(app, host='127.0.0.1', port=PORT)
