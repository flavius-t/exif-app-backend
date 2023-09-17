
USERNAME_FIELD = "username"
PASSWORD_FIELD = "password"


class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self) -> str:
        return f"User({self.username}, {self.password})"
