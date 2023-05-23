from util import debug
from pam import pam


def auth_pam(user: str, secret: str, pam_module: str) -> bool:
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
