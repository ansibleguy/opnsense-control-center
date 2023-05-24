from hashlib import sha256
from base64 import b64decode, b64encode
from Crypto import Random
from Crypto.Cipher import AES
from binascii import Error as BinasciiError

from config import ENCRYPTION_KEY

# just in case - if user supplied bad encryption-key
SALT = b'6xdTnXZ6xUEJE7gKnOZf7whJRa99nP8HiF0DvxcE84YaFhQvzvAzvs5qwAT8irhjj55dPAjW5bF2P6Xb6DbGHSFuJ7zeonisCffW'

KEY = sha256(ENCRYPTION_KEY.encode() + SALT).digest()


def _pad(s: str):
    bs = AES.block_size
    return s + (bs - len(s) % bs) * chr(bs - len(s) % bs)


def _unpad(s: bytes):
    return s[:-ord(s[len(s)-1:])]


def encrypt(raw: str):
    raw = _pad(raw)
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    return b64encode(iv + cipher.encrypt(raw.encode()))


def decrypt(enc: str):
    try:
        enc = b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(KEY, AES.MODE_CBC, iv)
        return _unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    except (SystemError, BinasciiError):
        return None
