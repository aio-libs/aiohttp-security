import asyncio
import pytest

from aiohttp import web
from aiohttp_security import (remember, forget,
                              AbstractAuthorizationPolicy)
from aiohttp_security import setup as setup_security
from aiohttp_security.session_identity import SessionIdentityPolicy
from aiohttp_security.api import IDENTITY_KEY
from aiohttp_session import SimpleCookieStorage, get_session
from aiohttp_session import setup as setup_session


class Autz(AbstractAuthorizationPolicy):

    @asyncio.coroutine
    def permits(self, identity, permission, context=None):
        pass

    @asyncio.coroutine
    def authorized_userid(self, identity):
        pass


@pytest.fixture
def create_app_and_client2(create_app_and_client):
    @asyncio.coroutine
    def maker(*args, **kwargs):
        app, client = yield from create_app_and_client(*args, **kwargs)
        setup_session(app, SimpleCookieStorage())
        setup_security(app, SessionIdentityPolicy(), Autz())
        return app, client
    return maker


@pytest.mark.run_loop
def test_remember(create_app_and_client2):

    @asyncio.coroutine
    def handler(request):
        response = web.Response()
        yield from remember(request, response, 'Andrew')
        return response

    @asyncio.coroutine
    def check(request):
        session = yield from get_session(request)
        assert session['AIOHTTP_SECURITY'] == 'Andrew'
        return web.HTTPOk()

    app, client = yield from create_app_and_client2()
    app.router.add_route('GET', '/', handler)
    app.router.add_route('GET', '/check', check)
    resp = yield from client.get('/')
    assert 200 == resp.status
    yield from resp.release()

    resp = yield from client.get('/check')
    assert 200 == resp.status
    yield from resp.release()


@pytest.mark.run_loop
def test_identify(create_app_and_client2):

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

    app, client = yield from create_app_and_client2()
    app.router.add_route('GET', '/', check)
    app.router.add_route('POST', '/', create)
    resp = yield from client.post('/')
    assert 200 == resp.status
    yield from resp.release()

    resp = yield from client.get('/')
    assert 200 == resp.status
    yield from resp.release()


@pytest.mark.run_loop
def test_forget(create_app_and_client2):

    @asyncio.coroutine
    def index(request):
        session = yield from get_session(request)
        return web.HTTPOk(text=session.get('AIOHTTP_SECURITY', ''))

    @asyncio.coroutine
    def login(request):
        response = web.HTTPFound(location='/')
        yield from remember(request, response, 'Andrew')
        return response

    @asyncio.coroutine
    def logout(request):
        response = web.HTTPFound('/')
        yield from forget(request, response)
        return response

    app, client = yield from create_app_and_client2()
    app.router.add_route('GET', '/', index)
    app.router.add_route('POST', '/login', login)
    app.router.add_route('POST', '/logout', logout)

    resp = yield from client.post('/login')
    assert 200 == resp.status
    assert resp.url.endswith('/')
    txt = yield from resp.text()
    assert 'Andrew' == txt
    yield from resp.release()

    resp = yield from client.post('/logout')
    assert 200 == resp.status
    assert resp.url.endswith('/')
    txt = yield from resp.text()
    assert '' == txt
    yield from resp.release()
