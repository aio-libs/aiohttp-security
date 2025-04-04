import jwt
import pytest
from aiohttp import web

from aiohttp_security import AbstractAuthorizationPolicy
from aiohttp_security import setup as _setup
from aiohttp_security.api import IDENTITY_KEY
from aiohttp_security.jwt_identity import JWTIdentityPolicy


@pytest.fixture
def make_token():
    def factory(payload, secret):
        return jwt.encode(
            payload,
            secret,
            algorithm='HS256',
        )

    return factory


class Autz(AbstractAuthorizationPolicy):

    async def permits(self, identity, permission, context=None):
        pass

    async def authorized_userid(self, identity):
        pass


async def test_no_pyjwt_installed(mocker):
    mocker.patch("aiohttp_security.jwt_identity.HAS_JWT", False)
    with pytest.raises(RuntimeError):
        JWTIdentityPolicy('secret')


async def test_identify(make_token, aiohttp_client):
    kwt_secret_key = "Key"  # noqa: S105

    token = make_token({'login': 'Andrew'}, kwt_secret_key)

    async def check(request):
        policy = request.app[IDENTITY_KEY]
        identity = await policy.identify(request)
        assert "Andrew" == identity
        return web.Response()

    app = web.Application()
    _setup(app, JWTIdentityPolicy(kwt_secret_key), Autz())
    app.router.add_route('GET', '/', check)

    client = await aiohttp_client(app)
    headers = {"Authorization": "Bearer {}".format(token)}
    resp = await client.get('/', headers=headers)
    assert 200 == resp.status


async def test_identify_broken_scheme(make_token, aiohttp_client):
    kwt_secret_key = "Key"  # noqa: S105

    token = make_token({'login': 'Andrew'}, kwt_secret_key)

    async def check(request):
        policy = request.app[IDENTITY_KEY]

        try:
            await policy.identify(request)
        except ValueError as exc:
            raise web.HTTPBadRequest(reason=str(exc))

        return web.Response()

    app = web.Application()
    _setup(app, JWTIdentityPolicy(kwt_secret_key), Autz())
    app.router.add_route('GET', '/', check)

    client = await aiohttp_client(app)
    headers = {"Authorization": "Token {}".format(token)}
    resp = await client.get('/', headers=headers)
    assert 400 == resp.status
    assert 'Invalid authorization scheme' in resp.reason


async def test_identify_expired_signature(make_token, aiohttp_client):
    kwt_secret_key = "Key"  # noqa: S105

    token = make_token({"login": "Andrew", "exp": 0}, kwt_secret_key)

    async def check(request):
        policy = request.app[IDENTITY_KEY]
        try:
            await policy.identify(request)
        except jwt.exceptions.PyJWTError as exc:
            raise web.HTTPBadRequest(reason=str(exc))

        assert False

    app = web.Application()
    _setup(app, JWTIdentityPolicy(kwt_secret_key), Autz())
    app.router.add_route("GET", "/", check)

    client = await aiohttp_client(app)
    headers = {"Authorization": "Bearer {}".format(token)}
    resp = await client.get("/", headers=headers)
    assert 400 == resp.status
    assert "Signature has expired" in resp.reason
