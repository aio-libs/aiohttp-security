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

    async def permits(self, identity, permission, context=None):
        pass

    async def authorized_userid(self, identity):
        pass


@pytest.fixture
def make_app():
    app = web.Application()
    setup_session(app, SimpleCookieStorage())
    setup_security(app, SessionIdentityPolicy(), Autz())
    return app


async def test_remember(make_app, aiohttp_client):

    async def handler(request):
        response = web.Response()
        await remember(request, response, 'Andrew')
        return response

    async def check(request):
        session = await get_session(request)
        assert session['AIOHTTP_SECURITY'] == 'Andrew'
        return web.Response()

    app = make_app()
    app.router.add_route('GET', '/', handler)
    app.router.add_route('GET', '/check', check)
    client = await aiohttp_client(app)
    resp = await client.get('/')
    assert 200 == resp.status

    resp = await client.get('/check')
    assert 200 == resp.status


async def test_identify(make_app, aiohttp_client):

    async def create(request):
        response = web.Response()
        await remember(request, response, 'Andrew')
        return response

    async def check(request):
        policy = request.app[IDENTITY_KEY]
        user_id = await policy.identify(request)
        assert 'Andrew' == user_id
        return web.Response()

    app = make_app()
    app.router.add_route('GET', '/', check)
    app.router.add_route('POST', '/', create)
    client = await aiohttp_client(app)
    resp = await client.post('/')
    assert 200 == resp.status

    resp = await client.get('/')
    assert 200 == resp.status


async def test_forget(make_app, aiohttp_client):

    async def index(request):
        session = await get_session(request)
        return web.Response(text=session.get('AIOHTTP_SECURITY', ''))

    async def login(request):
        response = web.HTTPFound(location='/')
        await remember(request, response, 'Andrew')
        raise response

    async def logout(request):
        response = web.HTTPFound('/')
        await forget(request, response)
        raise response

    app = make_app()
    app.router.add_route('GET', '/', index)
    app.router.add_route('POST', '/login', login)
    app.router.add_route('POST', '/logout', logout)

    client = await aiohttp_client(app)

    resp = await client.post('/login')
    assert 200 == resp.status
    assert str(resp.url).endswith('/')
    txt = await resp.text()
    assert 'Andrew' == txt

    resp = await client.post('/logout')
    assert 200 == resp.status
    assert str(resp.url).endswith('/')
    txt = await resp.text()
    assert '' == txt
