import asyncio
import pytest

from aiohttp import web
from aiohttp_security import (remember, permits, get_user_identity,
                              AbstractAuthorizationPolicy)
from aiohttp_security import setup as _setup
from aiohttp_security.cookies_identity import CookiesIdentityPolicy


class Autz(AbstractAuthorizationPolicy):

    @asyncio.coroutine
    def permits(self, identity, permission, context=None):
        if identity == 'UserID':
            return permission in {'read', 'write'}
        else:
            return False

    '''
    @asyncio.coroutine
    def authorized_userid(self, identity):
        if identity == 'UserID':
            return 'Andrew'
        else:
            return None
    '''


@pytest.mark.run_loop
def test_authorized_userid(create_app_and_client):

    @asyncio.coroutine
    def login(request):
        response = web.HTTPFound(location='/')
        yield from remember(request, response, 'Andrew')
        return response

    @asyncio.coroutine
    def check(request):
        userid = yield from get_user_identity(request)
        assert 'Andrew' == userid
        return web.Response(text=userid)

    app, client = yield from create_app_and_client()
    _setup(app, CookiesIdentityPolicy(), Autz())
    app.router.add_route('GET', '/', check)
    app.router.add_route('POST', '/login', login)

    resp = yield from client.post('/login')
    assert 200 == resp.status
    txt = yield from resp.text()
    assert 'Andrew' == txt
    yield from resp.release()


@pytest.mark.run_loop
def test_authorized_userid_not_authorized(create_app_and_client):

    @asyncio.coroutine
    def check(request):
        userid = yield from get_user_identity(request)
        assert userid is None
        return web.Response()

    app, client = yield from create_app_and_client()
    _setup(app, CookiesIdentityPolicy(), Autz())
    app.router.add_route('GET', '/', check)
    resp = yield from client.get('/')
    assert 200 == resp.status
    yield from resp.release()


@pytest.mark.run_loop
def test_permits(create_app_and_client):

    @asyncio.coroutine
    def login(request):
        response = web.HTTPFound(location='/')
        yield from remember(request, response, 'UserID')
        return response

    @asyncio.coroutine
    def check(request):
        ret = yield from permits(request, 'read')
        assert ret
        ret = yield from permits(request, 'write')
        assert ret
        ret = yield from permits(request, 'unknown')
        assert not ret
        return web.Response()

    app, client = yield from create_app_and_client()
    _setup(app, CookiesIdentityPolicy(), Autz())
    app.router.add_route('GET', '/', check)
    app.router.add_route('POST', '/login', login)
    resp = yield from client.post('/login')
    assert 200 == resp.status
    yield from resp.release()


@pytest.mark.run_loop
def test_permits_unauthorized(create_app_and_client):

    @asyncio.coroutine
    def check(request):
        ret = yield from permits(request, 'read')
        assert not ret
        ret = yield from permits(request, 'write')
        assert not ret
        ret = yield from permits(request, 'unknown')
        assert not ret
        return web.Response()

    app, client = yield from create_app_and_client()
    _setup(app, CookiesIdentityPolicy(), Autz())
    app.router.add_route('GET', '/', check)
    resp = yield from client.get('/')
    assert 200 == resp.status
    yield from resp.release()
