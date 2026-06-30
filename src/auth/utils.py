import bcrypt


"""
    Did not follow the same approach as in the tutorial as passlib library is not under active maintenance
"""


def hash_password(password: str) -> str:
    # Convert string to bytes
    password_bytes = password.encode("utf-8")
    
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    
    # Decode back to a UTF-8 string to safely save in our database
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(password: str, stored_hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), stored_hashed.encode("utf-8"))