import string
import secrets


def generate_password(length: int = 12) -> str:
    """Generate a random password that includes at least one lowercase letter,
    one uppercase letter, one digit, and one symbol."""
    if length < 4:
        raise ValueError("Password length must be at least 4 to include every character type.")

    alphabet = string.ascii_letters + string.digits + string.punctuation

    while True:
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        if (any(c.islower() for c in password)
                and any(c.isupper() for c in password)
                and any(c.isdigit() for c in password)
                and any(c in string.punctuation for c in password)):
            return password


def validate_fields(website: str, username: str, password: str) -> bool:
    """Return True only if none of the three fields are blank/whitespace-only."""
    return bool(website.strip()) and bool(username.strip()) and bool(password.strip())
