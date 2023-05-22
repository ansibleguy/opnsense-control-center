from config import DEBUG


def debug(msg: str, loc: str = None):
    if DEBUG:
        if loc is not None:
            print(f'DEBUG: /{loc} | {msg}')

        else:
            print(f'DEBUG: {msg}')
