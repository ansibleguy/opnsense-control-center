# {{ ansible_managed }}
# ansibleguy: opnsense-control-center

import ssl
from pathlib import Path

import ldap3
from yaml import safe_load as yaml_safe_load

from config import LDAP_CONFIG_FILE
from util import debug

# see: https://www.python-ldap.org/_/downloads/en/python-ldap-3.3.0/pdf/

# some providers like google don't support all attributes
LDAP_ATTRIBUTE_IGNORE = [
    'createTimestamp',
    'modifyTimestamp',
]
LDAP_IP_MODE_MAPPING = {
    4: ldap3.IP_V4_ONLY,
    6: ldap3.IP_V6_ONLY,
    46: ldap3.IP_V4_PREFERRED,
    64: ldap3.IP_V6_PREFERRED,
}
LDAP_TLS_VERSION_MAPPING = {
    1.0: ssl.PROTOCOL_TLSv1,
    1.1: ssl.PROTOCOL_TLSv1_1,
    1.2: ssl.PROTOCOL_TLSv1_2,
}


def _server(config: dict) -> ldap3.Server:
    mode = ldap3.IP_SYSTEM_DEFAULT

    if config['ip_version'] in LDAP_IP_MODE_MAPPING:
        mode = LDAP_IP_MODE_MAPPING[config['ip_version']]

    if config['tls']:
        return ldap3.Server(
            host=config['server'],
            tls=_tls(config),
            mode=mode,
            port=config['port'],
            use_ssl=True,
        )

    return ldap3.Server(
        host=config['server'],
        mode=mode,
        port=config['port'],
        use_ssl=False,
    )


def _tls_set_cert(config: dict, ssl_context: dict, ctx_key: str, config_key: str):
    try:
        if Path(config[config_key]).exists():
            ssl_context[ctx_key] = config[config_key + '_file']

        else:
            ssl_context[ctx_key] = config[config_key + '_data']

    except OSError:
        ssl_context[ctx_key] = config[config_key + '_data']


def _tls(config: dict) -> ldap3.Tls:
    tls_version = ssl.PROTOCOL_TLS

    if config['tls_version'] in LDAP_TLS_VERSION_MAPPING:
        tls_version = LDAP_TLS_VERSION_MAPPING[config['tls_version']]

    ssl_context = {
        'validate': ssl.CERT_REQUIRED,
        'version': tls_version,
    }

    _tls_set_cert(config=config, ssl_context=ssl_context, ctx_key='ca_certs', config_key='ca')

    ldap3.set_config_parameter(
        'ATTRIBUTES_EXCLUDED_FROM_CHECK',
        ldap3.get_config_parameter('ATTRIBUTES_EXCLUDED_FROM_CHECK') +
        LDAP_ATTRIBUTE_IGNORE +
        config['ignore_attrs']
    )

    if config['use_client_cert']:
        _tls_set_cert(config=config, ssl_context=ssl_context, ctx_key='local_certificate', config_key='client_cert')
        _tls_set_cert(config=config, ssl_context=ssl_context, ctx_key='local_private_key', config_key='client_key')
        if config['client_key_pwd'] not in ['', ' ', None]:
            ssl_context['local_private_key_password'] = config['client_key_pwd']

    return ldap3.Tls(**ssl_context)


def auth_ldap(user: str, secret: str) -> bool:
    with open(LDAP_CONFIG_FILE, 'r', encoding='utf-8') as config_file:
        config = yaml_safe_load(config_file.read())

    server = _server(config)
    ldap = ldap3.Connection(
        server=server,
        user=config['bind']['user'],
        password=config['bind']['pwd'],
    )

    # bind with service user to check if user is authorized
    ldap.open()
    if ldap.bind():
        debug('AUTH LDAP | Bind user | Authentication successful')
        ldap.search(
            search_base=config['base_dn'],
            search_filter=config['filter'],
        )
        if len(ldap.entries) == 1:
            print(f"AUTH LDAP | User '{user}' | Authorized")
            ldap_user = ldap.entries[0]
            debug(f"AUTH LDAP | User '{user}' | Matched filter: '{config['filter']}'")

            # validate actual user credentials
            login_test = ldap3.Connection(
                server=server,
                user=ldap_user.entry_dn,
                password=secret,
            )
            login_test.open()

            if login_test.bind():
                login_test.unbind()
                print(f"AUTH LDAP | User '{user}' | Authentication successful")
                return True

            print(f"AUTH LDAP | User '{user}' | Authentication failed")

        else:
            print(f"AUTH LDAP | User '{user}' | Unauthorized")

    else:
        print('AUTH LDAP | Bind User | Authentication failed')

    return False
