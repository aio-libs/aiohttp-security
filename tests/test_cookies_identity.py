from aiohttp import web
from aiohttp_security import (remember, forget,
                              AbstractAuthorizationPolicy)
from aiohttp_security import setup as _setup
from aiohttp_security.cookies_identity import CookiesIdentityPolicy
from aiohttp_security.api import IDENTITY_KEY


class Autz(AbstractAuthorizationPolicy):

    async def permits(self, identity, permission, context=None):
        pass

    async def authorized_userid(self, identity):
        pass


async def test_remember(loop, aiohttp_client):

    async def handler(request):
        response = web.Response()
        await remember(request, response, 'Andrew')
        return response

    app = web.Application()
    _setup(app, CookiesIdentityPolicy(), Autz())
    app.router.add_route('GET', '/', handler)
    client = await aiohttp_client(app)
    resp = await client.get('/')
    assert 200 == resp.status
    assert 'Andrew' == resp.cookies['AIOHTTP_SECURITY'].value


async def test_identify(loop, aiohttp_client):

    async def create(request):
        response = web.Response()
        await remember(request, response, 'Andrew')
        return response

    async def check(request):
        policy = request.app[IDENTITY_KEY]
        user_id = await policy.identify(request)
        assert 'Andrew' == user_id
        return web.Response()

    app = web.Application()
    _setup(app, CookiesIdentityPolicy(), Autz())
    app.router.add_route('GET', '/', check)
    app.router.add_route('POST', '/', create)
    client = await aiohttp_client(app)
    resp = await client.post('/')
    assert 200 == resp.status
    await resp.release()
    resp = await client.get('/')
    assert 200 == resp.status


async def test_forget(loop, aiohttp_client):

    async def index(request):
        return web.Response()

    async def login(request):
        response = web.HTTPFound(location='/')
        await remember(request, response, 'Andrew')
        raise response

    async def logout(request):
        response = web.HTTPFound(location='/')
        await forget(request, response)
        raise response

    app = web.Application()
    _setup(app, CookiesIdentityPolicy(), Autz())
    app.router.add_route('GET', '/', index)
    app.router.add_route('POST', '/login', login)
    app.router.add_route('POST', '/logout', logout)
    client = await aiohttp_client(app)
    resp = await client.post('/login')
    assert 200 == resp.status
    assert str(resp.url).endswith('/')
    cookies = client.session.cookie_jar.filter_cookies(
        client.make_url('/'))
    assert 'Andrew' == cookies['AIOHTTP_SECURITY'].value

    resp = await client.post('/logout')
    assert 200 == resp.status
    assert str(resp.url).endswith('/')
    cookies = client.session.cookie_jar.filter_cookies(
        client.make_url('/'))
    assert 'AIOHTTP_SECURITY' not in cookies
