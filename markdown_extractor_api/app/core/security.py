import secrets
import hashlib
import typing
import bcrypt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # bcrypt requires bytes, so we encode the strings to utf-8
    return bcrypt.checkpw(
        plain_password.encode('utf-8'), 
        hashed_password.encode('utf-8')
    )

def get_password_hash(password: str) -> str:
    # Generate the salt and hash the password
    hashed_bytes = bcrypt.hashpw(
        password.encode('utf-8'), 
        bcrypt.gensalt()
    )
    # bcrypt returns bytes, so we decode it to a string to save in PostgreSQL
    return hashed_bytes.decode('utf-8')

def generate_api_key() -> typing.Tuple[str, str, str]:
    raw_token = secrets.token_hex(32)
    raw_api_key = f"mkd_{raw_token}"
    key_prefix = raw_api_key[:12]
    hashed_key = hashlib.sha256(raw_api_key.encode()).hexdigest()
    return raw_api_key, key_prefix, hashed_key