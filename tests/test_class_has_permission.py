from aiohttp import web
from aiohttp_security import setup as _setup
from aiohttp_security import (AbstractAuthorizationPolicy,
                              forget, class_has_permission,
                              remember)
from aiohttp_security.cookies_identity import CookiesIdentityPolicy


class Autz(AbstractAuthorizationPolicy):

    user_permission_map = {
        'user_1': {'bike.read'},
        'user_2': {'bike.create'},
        'user_3': {'bike.update'},
        'user_4': {'bike.delete'}
    }

    async def permits(self, identity, permission, context=None):
        if identity in self.user_permission_map:
            return permission in self.user_permission_map[identity]
        else:
            return False

    async def authorized_userid(self, identity):
        if identity in self.user_permission_map:
            return identity
        else:
            return None


async def test_class_has_permission(loop, test_client):

    @class_has_permission('bike')
    class BikeView(web.View):

        async def get(self):
            return web.HTTPOk()

        async def post(self):
            return web.HTTPOk()

        async def put(self):
            return web.HTTPOk()

        async def patch(self):
            return web.HTTPOk()

        async def delete(self):
            return web.HTTPOk()

    class SessionView(web.View):
        async def post(self):
            user = self.request.match_info.get('user')
            response = web.HTTPFound(location='/')
            await remember(self.request, response, user)
            return response

        async def delete(self):
            response = web.HTTPFound(location='/')
            await forget(self.request, response)
            return response

    app = web.Application(loop=loop)
    _setup(app, CookiesIdentityPolicy(), Autz())

    app.router.add_route(
        '*', '/permission', BikeView)
    app.router.add_route(
        '*', '/session/{user}', SessionView)

    client = await test_client(app)

    resp = await client.get('/permission')
    assert web.HTTPUnauthorized.status_code == resp.status
    resp = await client.post('/permission')
    assert web.HTTPUnauthorized.status_code == resp.status
    resp = await client.delete('/permission')
    assert web.HTTPUnauthorized.status_code == resp.status

    await client.post('/session/user_1')
    resp = await client.get('/permission')
    assert web.HTTPOk.status_code == resp.status
    resp = await client.post('/permission')
    assert web.HTTPForbidden.status_code == resp.status
    resp = await client.put('/permission')
    assert web.HTTPForbidden.status_code == resp.status
    resp = await client.patch('/permission')
    assert web.HTTPForbidden.status_code == resp.status
    resp = await client.delete('/permission')
    assert web.HTTPForbidden.status_code == resp.status

    await client.post('/session/user_2')
    resp = await client.get('/permission')
    assert web.HTTPForbidden.status_code == resp.status
    resp = await client.post('/permission')
    assert web.HTTPOk.status_code == resp.status
    resp = await client.put('/permission')
    assert web.HTTPForbidden.status_code == resp.status
    resp = await client.patch('/permission')
    assert web.HTTPForbidden.status_code == resp.status
    resp = await client.delete('/permission')
    assert web.HTTPForbidden.status_code == resp.status

    await client.post('/session/user_3')
    resp = await client.get('/permission')
    assert web.HTTPForbidden.status_code == resp.status
    resp = await client.post('/permission')
    assert web.HTTPForbidden.status_code == resp.status
    resp = await client.put('/permission')
    assert web.HTTPOk.status_code == resp.status
    resp = await client.patch('/permission')
    assert web.HTTPOk.status_code == resp.status
    resp = await client.delete('/permission')
    assert web.HTTPForbidden.status_code == resp.status

    await client.post('/session/user_4')
    resp = await client.get('/permission')
    assert web.HTTPForbidden.status_code == resp.status
    resp = await client.post('/permission')
    assert web.HTTPForbidden.status_code == resp.status
    resp = await client.put('/permission')
    assert web.HTTPForbidden.status_code == resp.status
    resp = await client.patch('/permission')
    assert web.HTTPForbidden.status_code == resp.status
    resp = await client.delete('/permission')
    assert web.HTTPOk.status_code == resp.status

    await client.delete('/session/user_4')
    resp = await client.get('/permission')
    assert web.HTTPUnauthorized.status_code == resp.status
    resp = await client.post('/permission')
    assert web.HTTPUnauthorized.status_code == resp.status
    resp = await client.put('/permission')
    assert web.HTTPUnauthorized.status_code == resp.status
    resp = await client.patch('/permission')
    assert web.HTTPUnauthorized.status_code == resp.status
    resp = await client.delete('/permission')
    assert web.HTTPUnauthorized.status_code == resp.status
