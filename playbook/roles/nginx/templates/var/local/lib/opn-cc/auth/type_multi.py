# {{ ansible_managed }}
# ansibleguy: opnsense-control-center

from type_pam import auth_system, auth_totp
from type_ldap import auth_ldap

MFA_USER_AUTH_MAPPING = {
    'ldap': auth_ldap,
    'system': auth_system,
}
MFA_TOKEN_AUTH_MAPPING = {
    'totp': auth_totp,
}


def auth_multi(
        user: str, secret_user: str, secret_token: str,
        user_auth: str, token_auth: str = 'totp',
) -> bool:
    auth1 = MFA_USER_AUTH_MAPPING[user_auth](user=user, secret=secret_user)

    if not auth1:
        return False

    return MFA_TOKEN_AUTH_MAPPING[token_auth](user=user, secret=secret_token)
