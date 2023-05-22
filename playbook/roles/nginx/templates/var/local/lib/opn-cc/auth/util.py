from config import DEBUG


def debug(loc: str, msg: str):
    if DEBUG:
        print(f'DEBUG: /{loc} | {msg}')
