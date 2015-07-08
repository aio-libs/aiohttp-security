import asyncio

from aiohttp_security.authorization import AbstractAuthorizationPolicy


class DictionaryAuthorizationPolicy(AbstractAuthorizationPolicy):
    def __init__(self, data):
        self.data = data

    @asyncio.coroutine
    def permits(self, identity, permission, context=None):
        record = self.data.get(identity)
        if record is not None:
            # TODO: implement actual permission checker
            if permission in record:
                return True
        return False

    @asyncio.coroutine
    def authorized_user_id(self, identity):
        return identity if identity in self.data else None
