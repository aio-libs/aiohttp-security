from typing import NamedTuple, Tuple


class User(NamedTuple):
    username: str
    password: str
    permissions: Tuple[str, ...]


user_map = {
    user.username: user for user in [
        User('devin', 'password', ('public',)),
        User('jack', 'password', ('public', 'protected',)),
    ]
}
