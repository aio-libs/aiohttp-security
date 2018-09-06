"""Identity policy for storing info in the jwt token.

"""

from .abc import AbstractIdentityPolicy

try:
    import jwt
except ImportError:  # pragma: no cover
    jwt = None


AUTH_HEADER_NAME = 'Authorization'
AUTH_SCHEME = 'Bearer '


class JWTIdentityPolicy(AbstractIdentityPolicy):
    def __init__(self, secret, algorithm='HS256'):
        if jwt is None:
            raise RuntimeError('Please install `PyJWT`')
        self.secret = secret
        self.algorithm = algorithm

    async def identify(self, request):
        header_identity = request.headers.get(AUTH_HEADER_NAME)

        if header_identity is None:
            return

        if not header_identity.startswith(AUTH_SCHEME):
            raise ValueError('Invalid authorization scheme. ' +
                             'Should be `Bearer <token>`')

        token = header_identity.split(' ')[1].strip()

        identity = jwt.decode(token,
                              self.secret,
                              algorithms=[self.algorithm])
        return identity

    async def remember(self, *args, **kwargs):  # pragma: no cover
        pass

    async def forget(self, request, response):  # pragma: no cover
        pass
