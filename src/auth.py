import bcrypt

# simple demo users
users = {
    "admin": {
        "password": bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()),
        "role": "admin"
    },
    "user": {
        "password": bcrypt.hashpw("user123".encode(), bcrypt.gensalt()),
        "role": "user"
    }
}

def authenticate(username, password):

    if username in users:
        stored_password = users[username]["password"]

        if bcrypt.checkpw(password.encode(), stored_password):
            return users[username]["role"]

    return None