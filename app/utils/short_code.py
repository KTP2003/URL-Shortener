import secrets

BASE62_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


def generate_short_code(length: int = 8) -> str:
    """Generate a random Base62 string of the specified length."""
    return ''.join(secrets.choice(BASE62_ALPHABET) for _ in range(length))
