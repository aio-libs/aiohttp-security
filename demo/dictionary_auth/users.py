from collections import namedtuple


User = namedtuple("User", ["username", "password", "permissions"])

user_map = {
    user.username: user
    for user in [
        User("devin", "password", ("public",)),
        User(
            "jack",
            "password",
            (
                "public",
                "protected",
            ),
        ),
    ]
}
