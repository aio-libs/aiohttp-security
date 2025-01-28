"""Identity policy for storing info in the jwt token.

"""

from typing import Optional

from aiohttp import web

from .abc import AbstractIdentityPolicy

try:
    import jwt
    HAS_JWT = True
    _bases_error = (jwt.exceptions.PyJWTError, ValueError)
except ImportError:  # pragma: no cover
    HAS_JWT = False
    _bases_error = (ValueError, )


AUTH_HEADER_NAME = 'Authorization'
AUTH_SCHEME = 'Bearer '


# This class inherits from ValueError to maintain backward compatibility
# with previous versions of aiohttp-security
class InvalidAuthorizationScheme(*_bases_error):
    pass


class JWTIdentityPolicy(AbstractIdentityPolicy):
    def __init__(self, secret: str, algorithm: str = "HS256", key: str = "login"):
        if not HAS_JWT:
            raise RuntimeError('Please install `PyJWT`')
        self.secret = secret
        self.algorithm = algorithm
        self.key = key

    async def identify(self, request: web.Request) -> Optional[str]:
        header_identity = request.headers.get(AUTH_HEADER_NAME)

        if header_identity is None:
            return None

        if not header_identity.startswith(AUTH_SCHEME):
            raise InvalidAuthorizationScheme("Invalid authorization scheme. "
                                             "Should be `{}<token>`".format(AUTH_SCHEME))

        token = header_identity.split(' ')[1].strip()

        identity = jwt.decode(token,
                              self.secret,
                              algorithms=[self.algorithm])
        return identity.get(self.key)  # type: ignore[no-any-return]

    async def remember(self, request: web.Request, response: web.StreamResponse,
                       identity: str, **kwargs: None) -> None:
        pass

    async def forget(self, request: web.Request, response: web.StreamResponse) -> None:
        pass
