import enum

from aiohttp import web
from aiohttp_security import setup as _setup
from aiohttp_security import (AbstractAuthorizationPolicy, authorized_userid,
                              forget, has_permission, is_anonymous,
                              login_required, permits, remember)
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


async def test_authorized_userid(loop, test_client):

    async def login(request):
        response = web.HTTPFound(location='/')
        await remember(request, response, 'UserID')
        return response

    async def check(request):
        userid = await authorized_userid(request)
        assert 'Andrew' == userid
        return web.Response(text=userid)

    app = web.Application(loop=loop)
    _setup(app, CookiesIdentityPolicy(), Autz())
    app.router.add_route('GET', '/', check)
    app.router.add_route('POST', '/login', login)
    client = await test_client(app)

    resp = await client.post('/login')
    assert 200 == resp.status
    txt = await resp.text()
    assert 'Andrew' == txt


async def test_authorized_userid_not_authorized(loop, test_client):

    async def check(request):
        userid = await authorized_userid(request)
        assert userid is None
        return web.Response()

    app = web.Application(loop=loop)
    _setup(app, CookiesIdentityPolicy(), Autz())
    app.router.add_route('GET', '/', check)
    client = await test_client(app)

    resp = await client.get('/')
    assert 200 == resp.status


async def test_permits_enum_permission(loop, test_client):
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
        return response

    async def check(request):
        ret = await permits(request, Permission.READ)
        assert ret
        ret = await permits(request, Permission.WRITE)
        assert ret
        ret = await permits(request, Permission.UNKNOWN)
        assert not ret
        return web.Response()

    app = web.Application(loop=loop)
    _setup(app, CookiesIdentityPolicy(), Autz())
    app.router.add_route('GET', '/', check)
    app.router.add_route('POST', '/login', login)
    client = await test_client(app)
    resp = await client.post('/login')
    assert 200 == resp.status


async def test_permits_unauthorized(loop, test_client):

    async def check(request):
        ret = await permits(request, 'read')
        assert not ret
        ret = await permits(request, 'write')
        assert not ret
        ret = await permits(request, 'unknown')
        assert not ret
        return web.Response()

    app = web.Application(loop=loop)
    _setup(app, CookiesIdentityPolicy(), Autz())
    app.router.add_route('GET', '/', check)
    client = await test_client(app)
    resp = await client.get('/')
    assert 200 == resp.status


async def test_is_anonymous(loop, test_client):

    async def index(request):
        is_anon = await is_anonymous(request)
        if is_anon:
            return web.HTTPUnauthorized()
        return web.HTTPOk()

    async def login(request):
        response = web.HTTPFound(location='/')
        await remember(request, response, 'UserID')
        return response

    async def logout(request):
        response = web.HTTPFound(location='/')
        await forget(request, response)
        return response

    app = web.Application(loop=loop)
    _setup(app, CookiesIdentityPolicy(), Autz())
    app.router.add_route('GET', '/', index)
    app.router.add_route('POST', '/login', login)
    app.router.add_route('POST', '/logout', logout)
    client = await test_client(app)
    resp = await client.get('/')
    assert web.HTTPUnauthorized.status_code == resp.status

    await client.post('/login')
    resp = await client.get('/')
    assert web.HTTPOk.status_code == resp.status

    await client.post('/logout')
    resp = await client.get('/')
    assert web.HTTPUnauthorized.status_code == resp.status


async def test_login_required(loop, test_client):
    @login_required
    async def index(request):
        return web.HTTPOk()

    async def login(request):
        response = web.HTTPFound(location='/')
        await remember(request, response, 'UserID')
        return response

    async def logout(request):
        response = web.HTTPFound(location='/')
        await forget(request, response)
        return response

    app = web.Application(loop=loop)
    _setup(app, CookiesIdentityPolicy(), Autz())
    app.router.add_route('GET', '/', index)
    app.router.add_route('POST', '/login', login)
    app.router.add_route('POST', '/logout', logout)
    client = await test_client(app)
    resp = await client.get('/')
    assert web.HTTPUnauthorized.status_code == resp.status

    await client.post('/login')
    resp = await client.get('/')
    assert web.HTTPOk.status_code == resp.status

    await client.post('/logout')
    resp = await client.get('/')
    assert web.HTTPUnauthorized.status_code == resp.status


async def test_login_required_with_class_view(loop, test_client):

    class IndexView(web.View):
        @login_required
        async def get(self):
            return web.HTTPOk()

    async def login(request):
        response = web.HTTPFound(location='/')
        await remember(request, response, 'UserID')
        return response

    async def logout(request):
        response = web.HTTPFound(location='/')
        await forget(request, response)
        return response

    app = web.Application(loop=loop)
    _setup(app, CookiesIdentityPolicy(), Autz())
    app.router.add_route('*', '/', IndexView)
    app.router.add_route('POST', '/login', login)
    app.router.add_route('POST', '/logout', logout)
    client = await test_client(app)
    resp = await client.get('/')
    assert web.HTTPUnauthorized.status_code == resp.status

    await client.post('/login')
    resp = await client.get('/')
    assert web.HTTPOk.status_code == resp.status

    await client.post('/logout')
    resp = await client.get('/')
    assert web.HTTPUnauthorized.status_code == resp.status


async def test_has_permission(loop, test_client):

    @has_permission('read')
    async def index_read(request):
        return web.HTTPOk()

    @has_permission('write')
    async def index_write(request):
        return web.HTTPOk()

    @has_permission('forbid')
    async def index_forbid(request):
        return web.HTTPOk()

    async def login(request):
        response = web.HTTPFound(location='/')
        await remember(request, response, 'UserID')
        return response

    async def logout(request):
        response = web.HTTPFound(location='/')
        await forget(request, response)
        return response

    app = web.Application(loop=loop)
    _setup(app, CookiesIdentityPolicy(), Autz())
    app.router.add_route('GET', '/permission/read', index_read)
    app.router.add_route('GET', '/permission/write', index_write)
    app.router.add_route('GET', '/permission/forbid', index_forbid)
    app.router.add_route('POST', '/login', login)
    app.router.add_route('POST', '/logout', logout)
    client = await test_client(app)

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


async def test_has_permission_with_class_view(loop, test_client):

    class IndexView(web.View):
        @has_permission('read')
        async def get(self):
            return web.HTTPOk()

        @has_permission('write')
        async def post(self):
            return web.HTTPOk()

        @has_permission('forbid')
        async def delete(self):
            return web.HTTPOk()

    class SessionView(web.View):
        async def post(self):
            response = web.HTTPFound(location='/')
            await remember(self.request, response, 'UserID')
            return response

        async def delete(self):
            response = web.HTTPFound(location='/')
            await forget(self.request, response)
            return response

    app = web.Application(loop=loop)
    _setup(app, CookiesIdentityPolicy(), Autz())

    app.router.add_route(
        '*', '/permission', IndexView)
    app.router.add_route(
        '*', '/session', SessionView)

    client = await test_client(app)

    resp = await client.get('/permission')
    assert web.HTTPUnauthorized.status_code == resp.status
    resp = await client.post('/permission')
    assert web.HTTPUnauthorized.status_code == resp.status
    resp = await client.delete('/permission')
    assert web.HTTPUnauthorized.status_code == resp.status

    await client.post('/session')
    resp = await client.get('/permission')
    assert web.HTTPOk.status_code == resp.status
    resp = await client.post('/permission')
    assert web.HTTPOk.status_code == resp.status
    resp = await client.delete('/permission')
    assert web.HTTPForbidden.status_code == resp.status

    await client.delete('/session')
    resp = await client.get('/permission')
    assert web.HTTPUnauthorized.status_code == resp.status
    resp = await client.post('/permission')
    assert web.HTTPUnauthorized.status_code == resp.status
    resp = await client.delete('/permission')
    assert web.HTTPUnauthorized.status_code == resp.status
