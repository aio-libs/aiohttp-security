"""Identity policy for storing info in the jwt token.

"""

from typing import Optional

from aiohttp import web

from .abc import AbstractIdentityPolicy

try:
    import jwt
    HAS_JWT = True
except ImportError:  # pragma: no cover
    HAS_JWT = False


AUTH_HEADER_NAME = 'Authorization'
AUTH_SCHEME = 'Bearer '


class JWTIdentityPolicy(AbstractIdentityPolicy):
    def __init__(self, secret: str, algorithm: str = 'HS256'):
        if not HAS_JWT:
            raise RuntimeError('Please install `PyJWT`')
        self.secret = secret
        self.algorithm = algorithm

    async def identify(self, request: web.Request) -> Optional[str]:
        header_identity = request.headers.get(AUTH_HEADER_NAME)

        if header_identity is None:
            return None

        if not header_identity.startswith(AUTH_SCHEME):
            raise ValueError('Invalid authorization scheme. ' +
                             'Should be `{}<token>`'.format(AUTH_SCHEME))

        token = header_identity.split(' ')[1].strip()

        identity = jwt.decode(token,
                              self.secret,
                              algorithms=[self.algorithm])
        return identity

    async def remember(self, request: web.Request, response: web.StreamResponse,
                       identity: str, **kwargs: None) -> None:
        pass

    async def forget(self, request: web.Request, response: web.StreamResponse) -> None:
        pass
