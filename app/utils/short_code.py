import secrets

BASE62_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


def encode(number: int) -> str:
    """Convert an integer to a Base62 string."""
    if number < 0:
        raise ValueError("Number must be non-negative")

    if number == 0:
        return BASE62_ALPHABET[0]

    result = []
    while number:
        number, remainder = divmod(number, 62)
        result.append(BASE62_ALPHABET[remainder])

    return ''.join(reversed(result))


def decode(base62_str: str) -> int:
    """Convert a Base62 string back to an integer."""
    number = 0
    for char in base62_str:
        number = number * 62 + BASE62_ALPHABET.index(char)
    return number


def generate_short_code(length: int = 8) -> str:
    """Generate a random Base62 string of the specified length."""
    return ''.join(secrets.choice(BASE62_ALPHABET) for _ in range(length))

