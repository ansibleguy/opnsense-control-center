# {{ ansible_managed }}
# ansibleguy: opnsense-control-center


def auth_system(user: str, pwd: str) -> bool:
    # TESTING:
    if user == 'opncc' and pwd == 'osef3uof':
        return True

    return False