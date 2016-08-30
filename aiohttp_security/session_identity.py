"""Identity policy for storing info into aiohttp_session session.

aiohttp_session.setup() should be called on application initialization
to configure aiohttp_session properly.
"""

import asyncio

from aiohttp_session import get_session

from .abc import AbstractIdentityPolicy


class SessionIdentityPolicy(AbstractIdentityPolicy):

    def __init__(self, session_key='AIOHTTP_SECURITY'):
        self._session_key = session_key

    @asyncio.coroutine
    def identify(self, request):
        session = yield from get_session(request)
        return session.get(self._session_key)

    @asyncio.coroutine
    def remember(self, request, response, identity, **kwargs):
        session = yield from get_session(request)
        session[self._session_key] = identity

    @asyncio.coroutine
    def forget(self, request, response):
        session = yield from get_session(request)
        session.pop(self._session_key, None)
