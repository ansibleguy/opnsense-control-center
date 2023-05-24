# {{ ansible_managed }}
# ansibleguy: opnsense-control-center

from util import debug
from pam import pam

from config import PAM_FILE_SYSTEM, PAM_FILE_TOTP


def _auth_pam(user: str, secret: str, pam_module: str) -> bool:
    print(f"AUTH PAM | Module '{pam_module}' | User '{user}'")
    pam_check = pam()
    pam_result = pam_check.authenticate(user, secret, service=pam_module)

    debug(
        msg=f"AUTH PAM | Module '{pam_module}' | User '{user}' | "
            f"Result: '{pam_check.code}' '{pam_check.reason}' '{pam_result}'"
    )

    if pam_result:
        print(f"AUTH PAM | Module '{pam_module}' | User '{user}' | Authentication successful")
        return True

    print(f"AUTH PAM | Module '{pam_module}' | User '{user}' | Authentication failed")
    return False


def auth_system(user: str, secret: str) -> bool:
    return _auth_pam(user=user, secret=secret, pam_module=PAM_FILE_SYSTEM)


def auth_totp(user: str, secret: str) -> bool:
    return _auth_pam(user=user, secret=secret, pam_module=PAM_FILE_TOTP)
