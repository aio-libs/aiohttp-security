import asyncio

from aiohttp import web
from aiohttp_security import (remember, forget,
                              AbstractAuthorizationPolicy)
from aiohttp_security import setup as _setup
from aiohttp_security.cookies_identity import CookiesIdentityPolicy
from aiohttp_security.api import IDENTITY_KEY


class Autz(AbstractAuthorizationPolicy):

    @asyncio.coroutine
    def permits(self, identity, permission, context=None):
        pass

    @asyncio.coroutine
    def authorized_userid(self, identity):
        pass


@asyncio.coroutine
def test_remember(loop, test_client):

    @asyncio.coroutine
    def handler(request):
        response = web.Response()
        yield from remember(request, response, 'Andrew')
        return response

    app = web.Application(loop=loop)
    _setup(app, CookiesIdentityPolicy(), Autz())
    app.router.add_route('GET', '/', handler)
    client = yield from test_client(app)
    resp = yield from client.get('/')
    assert 200 == resp.status
    assert 'Andrew' == resp.cookies['AIOHTTP_SECURITY'].value
    yield from resp.release()


@asyncio.coroutine
def test_identify(loop, test_client):

    @asyncio.coroutine
    def create(request):
        response = web.Response()
        yield from remember(request, response, 'Andrew')
        return response

    @asyncio.coroutine
    def check(request):
        policy = request.app[IDENTITY_KEY]
        user_id = yield from policy.identify(request)
        assert 'Andrew' == user_id
        return web.Response()

    app = web.Application(loop=loop)
    _setup(app, CookiesIdentityPolicy(), Autz())
    app.router.add_route('GET', '/', check)
    app.router.add_route('POST', '/', create)
    client = yield from test_client(app)
    resp = yield from client.post('/')
    assert 200 == resp.status
    yield from resp.release()
    resp = yield from client.get('/')
    assert 200 == resp.status
    yield from resp.release()


@asyncio.coroutine
def test_forget(loop, test_client):

    @asyncio.coroutine
    def index(request):
        return web.Response()

    @asyncio.coroutine
    def login(request):
        response = web.HTTPFound(location='/')
        yield from remember(request, response, 'Andrew')
        return response

    @asyncio.coroutine
    def logout(request):
        response = web.HTTPFound(location='/')
        yield from forget(request, response)
        return response

    app = web.Application(loop=loop)
    _setup(app, CookiesIdentityPolicy(), Autz())
    app.router.add_route('GET', '/', index)
    app.router.add_route('POST', '/login', login)
    app.router.add_route('POST', '/logout', logout)
    client = yield from test_client(app)
    resp = yield from client.post('/login')
    assert 200 == resp.status
    assert resp.url.endswith('/')
    cookies = client.session.cookie_jar.filter_cookies(
        client.make_url('/'))
    assert 'Andrew' == cookies['AIOHTTP_SECURITY'].value
    yield from resp.release()
    resp = yield from client.post('/logout')
    assert 200 == resp.status
    assert resp.url.endswith('/')
    cookies = client.session.cookie_jar.filter_cookies(
        client.make_url('/'))
    assert 'AIOHTTP_SECURITY' not in cookies
    yield from resp.release()
