import secrets
import string

def generate_random_password(length=5):
    characters = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(characters) for _ in range(length))
    
    return password