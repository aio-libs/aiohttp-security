from typing import Dict, NamedTuple, Optional, Tuple


class User(NamedTuple):
    username: str
    password: str
    permissions: Tuple[str, ...]


user_map: Dict[Optional[str], User] = {
    user.username: user for user in [
        User('devin', 'password', ('public',)),
        User('jack', 'password', ('public', 'protected',)),
    ]
}
