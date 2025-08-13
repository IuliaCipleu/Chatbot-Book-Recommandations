import bcrypt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), hash.encode())
    except Exception:
        return False
