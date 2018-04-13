"""Identity policy for storing info in the jwt token.

"""

from .abc import AbstractIdentityPolicy
try:
    import jwt
except ImportError:  # pragma: no cover
    jwt = None


AUTH_HEADER_NAME = 'Authorization'


class JWTIdentityPolicy(AbstractIdentityPolicy):
    def __init__(self, secret, algorithm=None):
        if jwt is None:
            raise RuntimeError("Please install pyjwt")
        self.secret = secret
        self.algorithm = 'HS256' if algorithm is None else algorithm

    async def identify(self, request):
        header_identity = request.headers.get(AUTH_HEADER_NAME)
        identity = jwt.decode(header_identity,
                              self.secret,
                              algorithm=self.algorithm)

        return identity['identity']

    async def remember(self, *args, **kwargs):  # pragma: no cover
        pass

    async def forget(self, request, response):  # pragma: no cover
        pass
