# {{ ansible_managed }}
# ansibleguy: opnsense-control-center

from config import PAM_FILE_TOTP
from type_pam import auth_pam


def auth_totp(user: str, secret: str) -> bool:
    return auth_pam(user=user, secret=secret, pam_module=PAM_FILE_TOTP)
