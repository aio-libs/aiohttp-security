import asyncio

from aiohttp import web
from aiohttp_security import (remember, is_anonymous, login_required, has_permission, forget,
                              authorized_userid, permits,
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

    @asyncio.coroutine
    def authorized_userid(self, identity):
        if identity == 'UserID':
            return 'Andrew'
        else:
            return None


@asyncio.coroutine
def test_authorized_userid(loop, test_client):

    @asyncio.coroutine
    def login(request):
        response = web.HTTPFound(location='/')
        yield from remember(request, response, 'UserID')
        return response

    @asyncio.coroutine
    def check(request):
        userid = yield from authorized_userid(request)
        assert 'Andrew' == userid
        return web.Response(text=userid)

    app = web.Application(loop=loop)
    _setup(app, CookiesIdentityPolicy(), Autz())
    app.router.add_route('GET', '/', check)
    app.router.add_route('POST', '/login', login)
    client = yield from test_client(app)

    resp = yield from client.post('/login')
    assert 200 == resp.status
    txt = yield from resp.text()
    assert 'Andrew' == txt
    yield from resp.release()


@asyncio.coroutine
def test_authorized_userid_not_authorized(loop, test_client):

    @asyncio.coroutine
    def check(request):
        userid = yield from authorized_userid(request)
        assert userid is None
        return web.Response()

    app = web.Application(loop=loop)
    _setup(app, CookiesIdentityPolicy(), Autz())
    app.router.add_route('GET', '/', check)
    client = yield from test_client(app)

    resp = yield from client.get('/')
    assert 200 == resp.status
    yield from resp.release()


@asyncio.coroutine
def test_permits(loop, test_client):

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

    app = web.Application(loop=loop)
    _setup(app, CookiesIdentityPolicy(), Autz())
    app.router.add_route('GET', '/', check)
    app.router.add_route('POST', '/login', login)
    client = yield from test_client(app)
    resp = yield from client.post('/login')
    assert 200 == resp.status
    yield from resp.release()


@asyncio.coroutine
def test_permits_unauthorized(loop, test_client):

    @asyncio.coroutine
    def check(request):
        ret = yield from permits(request, 'read')
        assert not ret
        ret = yield from permits(request, 'write')
        assert not ret
        ret = yield from permits(request, 'unknown')
        assert not ret
        return web.Response()

    app = web.Application(loop=loop)
    _setup(app, CookiesIdentityPolicy(), Autz())
    app.router.add_route('GET', '/', check)
    client = yield from test_client(app)
    resp = yield from client.get('/')
    assert 200 == resp.status
    yield from resp.release()


@asyncio.coroutine
def test_is_anonymous(loop, test_client):

    @asyncio.coroutine
    def index(request):
        is_anon = yield from is_anonymous(request)
        if is_anon:
            return web.HTTPUnauthorized()
        return web.HTTPOk()

    @asyncio.coroutine
    def login(request):
        response = web.HTTPFound(location='/')
        yield from remember(request, response, 'UserID')
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
    resp = yield from client.get('/')
    assert web.HTTPUnauthorized.status_code == resp.status

    yield from client.post('/login')
    resp = yield from client.get('/')
    assert web.HTTPOk.status_code == resp.status

    yield from client.post('/logout')
    resp = yield from client.get('/')
    assert web.HTTPUnauthorized.status_code == resp.status


@asyncio.coroutine
def test_login_required(loop, test_client):
    @login_required
    @asyncio.coroutine
    def index(request):
        return web.HTTPOk()

    @asyncio.coroutine
    def login(request):
        response = web.HTTPFound(location='/')
        yield from remember(request, response, 'UserID')
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
    resp = yield from client.get('/')
    assert web.HTTPUnauthorized.status_code == resp.status

    yield from client.post('/login')
    resp = yield from client.get('/')
    assert web.HTTPOk.status_code == resp.status

    yield from client.post('/logout')
    resp = yield from client.get('/')
    assert web.HTTPUnauthorized.status_code == resp.status


@asyncio.coroutine
def test_has_permission(loop, test_client):

    @has_permission('read')
    @asyncio.coroutine
    def index_read(request):
        return web.HTTPOk()

    @has_permission('write')
    @asyncio.coroutine
    def index_write(request):
        return web.HTTPOk()

    @has_permission('forbid')
    @asyncio.coroutine
    def index_forbid(request):
        return web.HTTPOk()

    @asyncio.coroutine
    def login(request):
        response = web.HTTPFound(location='/')
        yield from remember(request, response, 'UserID')
        return response

    @asyncio.coroutine
    def logout(request):
        response = web.HTTPFound(location='/')
        yield from forget(request, response)
        return response

    app = web.Application(loop=loop)
    _setup(app, CookiesIdentityPolicy(), Autz())
    app.router.add_route('GET', '/permission/read', index_read)
    app.router.add_route('GET', '/permission/write', index_write)
    app.router.add_route('GET', '/permission/forbid', index_forbid)
    app.router.add_route('POST', '/login', login)
    app.router.add_route('POST', '/logout', logout)
    client = yield from test_client(app)

    resp = yield from client.get('/permission/read')
    assert web.HTTPUnauthorized.status_code == resp.status
    resp = yield from client.get('/permission/write')
    assert web.HTTPUnauthorized.status_code == resp.status
    resp = yield from client.get('/permission/forbid')
    assert web.HTTPUnauthorized.status_code == resp.status

    yield from client.post('/login')
    resp = yield from client.get('/permission/read')
    assert web.HTTPOk.status_code == resp.status
    resp = yield from client.get('/permission/write')
    assert web.HTTPOk.status_code == resp.status
    resp = yield from client.get('/permission/forbid')
    assert web.HTTPForbidden.status_code == resp.status

    yield from client.post('/logout')
    resp = yield from client.get('/permission/read')
    assert web.HTTPUnauthorized.status_code == resp.status
    resp = yield from client.get('/permission/write')
    assert web.HTTPUnauthorized.status_code == resp.status
    resp = yield from client.get('/permission/forbid')
    assert web.HTTPUnauthorized.status_code == resp.status
