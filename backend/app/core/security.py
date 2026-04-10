import os

from cryptography.fernet import Fernet

_fernet_key: bytes = os.environ.get(
    "FERNET_KEY", Fernet.generate_key().decode()
).encode()
_fernet = Fernet(_fernet_key)


def encrypt(data: str) -> str:
    return _fernet.encrypt(data.encode()).decode()


def decrypt(token: str) -> str:
    return _fernet.decrypt(token.encode()).decode()
