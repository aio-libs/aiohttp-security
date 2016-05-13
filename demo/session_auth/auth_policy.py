import asyncio

from aiohttp_security.abc import AbstractAuthorizationPolicy


class StubAuthorizationPolicy(AbstractAuthorizationPolicy):
    @asyncio.coroutine
    def permits(self, identity, permission, context=None):
        if identity == permission:
            return True
        return False
