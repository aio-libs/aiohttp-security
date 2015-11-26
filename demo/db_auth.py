import asyncio

from aiohttp_security.authorization import AbstractAuthorizationPolicy


class DBAuthorizationPolicy(AbstractAuthorizationPolicy):
    def __init__(self, dbengine):
        self.dbengine = dbengine

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
        with (yield from self.dbengine) as conn:
            conn
        return identity if identity in self.data else None
