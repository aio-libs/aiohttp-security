import enum
import pytest

from aiohttp import web
from aiohttp_security import setup as _setup
from aiohttp_security import (AbstractAuthorizationPolicy, authorized_userid,
                              forget, has_permission, is_anonymous,
                              login_required, permits, remember,
                              check_authorized, check_permission)
from aiohttp_security.cookies_identity import CookiesIdentityPolicy


class Autz(AbstractAuthorizationPolicy):

    async def permits(self, identity, permission, context=None):
        if identity == 'UserID':
            return permission in {'read', 'write'}
        else:
            return False

    async def authorized_userid(self, identity):
        if identity == 'UserID':
            return 'Andrew'
        else:
            return None


async def test_authorized_userid(loop, aiohttp_client):

    async def login(request):
        response = web.HTTPFound(location='/')
        await remember(request, response, 'UserID')
        raise response

    async def check(request):
        userid = await authorized_userid(request)
        assert 'Andrew' == userid
        return web.Response(text=userid)

    app = web.Application()
    _setup(app, CookiesIdentityPolicy(), Autz())
    app.router.add_route('GET', '/', check)
    app.router.add_route('POST', '/login', login)
    client = await aiohttp_client(app)

    resp = await client.post('/login')
    assert 200 == resp.status
    txt = await resp.text()
    assert 'Andrew' == txt


async def test_authorized_userid_not_authorized(loop, aiohttp_client):

    async def check(request):
        userid = await authorized_userid(request)
        assert userid is None
        return web.Response()

    app = web.Application()
    _setup(app, CookiesIdentityPolicy(), Autz())
    app.router.add_route('GET', '/', check)
    client = await aiohttp_client(app)

    resp = await client.get('/')
    assert 200 == resp.status


async def test_permits_enum_permission(loop, aiohttp_client):
    class Permission(enum.Enum):
        READ = '101'
        WRITE = '102'
        UNKNOWN = '103'

    class Autz(AbstractAuthorizationPolicy):

        async def permits(self, identity, permission, context=None):
            if identity == 'UserID':
                return permission in {Permission.READ, Permission.WRITE}
            else:
                return False

        async def authorized_userid(self, identity):
            if identity == 'UserID':
                return 'Andrew'
            else:
                return None

    async def login(request):
        response = web.HTTPFound(location='/')
        await remember(request, response, 'UserID')
        raise response

    async def check(request):
        ret = await permits(request, Permission.READ)
        assert ret
        ret = await permits(request, Permission.WRITE)
        assert ret
        ret = await permits(request, Permission.UNKNOWN)
        assert not ret
        return web.Response()

    app = web.Application()
    _setup(app, CookiesIdentityPolicy(), Autz())
    app.router.add_route('GET', '/', check)
    app.router.add_route('POST', '/login', login)
    client = await aiohttp_client(app)
    resp = await client.post('/login')
    assert 200 == resp.status


async def test_permits_unauthorized(loop, aiohttp_client):

    async def check(request):
        ret = await permits(request, 'read')
        assert not ret
        ret = await permits(request, 'write')
        assert not ret
        ret = await permits(request, 'unknown')
        assert not ret
        return web.Response()

    app = web.Application()
    _setup(app, CookiesIdentityPolicy(), Autz())
    app.router.add_route('GET', '/', check)
    client = await aiohttp_client(app)
    resp = await client.get('/')
    assert 200 == resp.status


async def test_is_anonymous(loop, aiohttp_client):

    async def index(request):
        is_anon = await is_anonymous(request)
        if is_anon:
            raise web.HTTPUnauthorized()
        return web.Response()

    async def login(request):
        response = web.HTTPFound(location='/')
        await remember(request, response, 'UserID')
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
    resp = await client.get('/')
    assert web.HTTPUnauthorized.status_code == resp.status

    await client.post('/login')
    resp = await client.get('/')
    assert web.HTTPOk.status_code == resp.status

    await client.post('/logout')
    resp = await client.get('/')
    assert web.HTTPUnauthorized.status_code == resp.status


async def test_login_required(loop, aiohttp_client):
    with pytest.raises(DeprecationWarning):

        @login_required
        async def index(request):
            return web.Response()

        async def login(request):
            response = web.HTTPFound(location='/')
            await remember(request, response, 'UserID')
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
        resp = await client.get('/')
        assert web.HTTPUnauthorized.status_code == resp.status

        await client.post('/login')
        resp = await client.get('/')
        assert web.HTTPOk.status_code == resp.status

        await client.post('/logout')
        resp = await client.get('/')
        assert web.HTTPUnauthorized.status_code == resp.status


async def test_check_authorized(loop, aiohttp_client):
    async def index(request):
        await check_authorized(request)
        return web.Response()

    async def login(request):
        response = web.HTTPFound(location='/')
        await remember(request, response, 'UserID')
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
    resp = await client.get('/')
    assert web.HTTPUnauthorized.status_code == resp.status

    await client.post('/login')
    resp = await client.get('/')
    assert web.HTTPOk.status_code == resp.status

    await client.post('/logout')
    resp = await client.get('/')
    assert web.HTTPUnauthorized.status_code == resp.status


async def test_has_permission(loop, aiohttp_client):

    with pytest.warns(DeprecationWarning):

        @has_permission('read')
        async def index_read(request):
            return web.Response()

        @has_permission('write')
        async def index_write(request):
            return web.Response()

        @has_permission('forbid')
        async def index_forbid(request):
            return web.Response()

        async def login(request):
            response = web.HTTPFound(location='/')
            await remember(request, response, 'UserID')
            return response

        async def logout(request):
            response = web.HTTPFound(location='/')
            await forget(request, response)
            raise response

        app = web.Application()
        _setup(app, CookiesIdentityPolicy(), Autz())
        app.router.add_route('GET', '/permission/read', index_read)
        app.router.add_route('GET', '/permission/write', index_write)
        app.router.add_route('GET', '/permission/forbid', index_forbid)
        app.router.add_route('POST', '/login', login)
        app.router.add_route('POST', '/logout', logout)
        client = await aiohttp_client(app)

        resp = await client.get('/permission/read')
        assert web.HTTPUnauthorized.status_code == resp.status
        resp = await client.get('/permission/write')
        assert web.HTTPUnauthorized.status_code == resp.status
        resp = await client.get('/permission/forbid')
        assert web.HTTPUnauthorized.status_code == resp.status

        await client.post('/login')
        resp = await client.get('/permission/read')
        assert web.HTTPOk.status_code == resp.status
        resp = await client.get('/permission/write')
        assert web.HTTPOk.status_code == resp.status
        resp = await client.get('/permission/forbid')
        assert web.HTTPForbidden.status_code == resp.status

        await client.post('/logout')
        resp = await client.get('/permission/read')
        assert web.HTTPUnauthorized.status_code == resp.status
        resp = await client.get('/permission/write')
        assert web.HTTPUnauthorized.status_code == resp.status
        resp = await client.get('/permission/forbid')
        assert web.HTTPUnauthorized.status_code == resp.status


async def test_check_permission(loop, aiohttp_client):

    async def index_read(request):
        await check_permission(request, 'read')
        return web.Response()

    async def index_write(request):
        await check_permission(request, 'write')
        return web.Response()

    async def index_forbid(request):
        await check_permission(request, 'forbid')
        return web.Response()

    async def login(request):
        response = web.HTTPFound(location='/')
        await remember(request, response, 'UserID')
        raise response

    async def logout(request):
        response = web.HTTPFound(location='/')
        await forget(request, response)
        raise response

    app = web.Application()
    _setup(app, CookiesIdentityPolicy(), Autz())
    app.router.add_route('GET', '/permission/read', index_read)
    app.router.add_route('GET', '/permission/write', index_write)
    app.router.add_route('GET', '/permission/forbid', index_forbid)
    app.router.add_route('POST', '/login', login)
    app.router.add_route('POST', '/logout', logout)
    client = await aiohttp_client(app)

    resp = await client.get('/permission/read')
    assert web.HTTPUnauthorized.status_code == resp.status
    resp = await client.get('/permission/write')
    assert web.HTTPUnauthorized.status_code == resp.status
    resp = await client.get('/permission/forbid')
    assert web.HTTPUnauthorized.status_code == resp.status

    await client.post('/login')
    resp = await client.get('/permission/read')
    assert web.HTTPOk.status_code == resp.status
    resp = await client.get('/permission/write')
    assert web.HTTPOk.status_code == resp.status
    resp = await client.get('/permission/forbid')
    assert web.HTTPForbidden.status_code == resp.status

    await client.post('/logout')
    resp = await client.get('/permission/read')
    assert web.HTTPUnauthorized.status_code == resp.status
    resp = await client.get('/permission/write')
    assert web.HTTPUnauthorized.status_code == resp.status
    resp = await client.get('/permission/forbid')
    assert web.HTTPUnauthorized.status_code == resp.status
