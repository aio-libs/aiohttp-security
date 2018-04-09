import pytest
from aiohttp import web
from aiohttp_security import AbstractAuthorizationPolicy
from aiohttp_security import setup as _setup
from aiohttp_security.jwt_identity import JWTIdentityPolicy
from aiohttp_security.api import IDENTITY_KEY
import jwt


class Autz(AbstractAuthorizationPolicy):

    async def permits(self, identity, permission, context=None):
        pass

    async def authorized_userid(self, identity):
        pass


async def test_no_pyjwt_installed(mocker):
    mocker.patch('aiohttp_security.jwt_identity.jwt', None)
    with pytest.raises(RuntimeError):
        JWTIdentityPolicy('secret')


async def test_identify(loop, test_client):
    kwt_secret_key = 'Key'

    async def create(request):
        response = web.Response()
        data = await request.post()

        encoded_identity = jwt.encode({'identity': data['login']},
                                      kwt_secret_key,
                                      algorithm='HS256')

        response.text = encoded_identity.decode('utf-8')
        return response

    async def check(request):
        policy = request.app[IDENTITY_KEY]
        user_id = await policy.identify(request)
        assert 'Andrew' == user_id
        return web.Response()

    app = web.Application(loop=loop)
    _setup(app, JWTIdentityPolicy(kwt_secret_key), Autz())
    app.router.add_route('GET', '/', check)
    app.router.add_route('POST', '/', create)
    client = await test_client(app)
    resp = await client.post('/', data={'login': 'Andrew'})
    jwt_token = await resp.content.read()
    assert 200 == resp.status
    await resp.release()
    headers = {'Authorization': str(jwt_token.decode('utf-8'))}
    resp = await client.get('/', headers=headers)
    assert 200 == resp.status
