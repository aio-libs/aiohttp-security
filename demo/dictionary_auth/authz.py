from aiohttp_security.abc import AbstractAuthorizationPolicy


class DictionaryAuthorizationPolicy(AbstractAuthorizationPolicy):
    def __init__(self, user_map):
        super().__init__()
        self.user_map = user_map

    async def authorized_userid(self, identity):
        """Retrieve authorized user id.
        Return the user_id of the user identified by the identity
        or 'None' if no user exists related to the identity.
        """
        if identity in self.user_map:
            return identity

    async def permits(self, identity, permission, context=None):
        """Check user permissions.
        Return True if the identity is allowed the permission in the
        current context, else return False.
        """
        # pylint: disable=unused-argument
        user = self.user_map.get(identity)
        if not user:
            return False
        return permission in user.permissions


async def check_credentials(user_map, username, password):
    user = user_map.get(username)
    if not user:
        return False

    return user.password == password
