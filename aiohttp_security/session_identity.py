"""Identity policy for storing info into aiohttp_session session.

aiohttp_session.setup() should be called on application initialization
to configure aiohttp_session properly.
"""

try:
    from aiohttp_session import get_session
    HAS_AIOHTTP_SESSION = True
except ImportError:  # pragma: no cover
    HAS_AIOHTTP_SESSION = False

from .abc import AbstractIdentityPolicy


class SessionIdentityPolicy(AbstractIdentityPolicy):

    def __init__(self, session_key='AIOHTTP_SECURITY'):
        self._session_key = session_key

        if not HAS_AIOHTTP_SESSION:  # pragma: no cover
            raise ImportError(
                'SessionIdentityPolicy requires `aiohttp_session`')

    async def identify(self, request):
        session = await get_session(request)
        return session.get(self._session_key)

    async def remember(self, request, response, identity, **kwargs):
        session = await get_session(request)
        session[self._session_key] = identity

    async def forget(self, request, response):
        session = await get_session(request)
        session.pop(self._session_key, None)
