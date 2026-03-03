from aiohttp import web
import pytest

from aiohttp_security import authorized_userid, check_permission, permits


async def test_authorized_userid(aiohttp_client):

    async def check(request):
        userid = await authorized_userid(request)
        assert userid is None
        return web.Response()

    app = web.Application()
    app.router.add_route('GET', '/', check)
    client = await aiohttp_client(app)
    resp = await client.get('/')
    assert 200 == resp.status


async def test_permits(aiohttp_client):

    async def check(request):
        ret = await permits(request, 'read')
        assert ret
        ret = await permits(request, 'write')
        assert ret
        ret = await permits(request, 'unknown')
        assert ret
        return web.Response()

    app = web.Application()
    app.router.add_route('GET', '/', check)
    client = await aiohttp_client(app)
    resp = await client.get('/')
    assert 200 == resp.status


async def test_check_permission_rejects_invalid_value(aiohttp_client):

    async def check(request):
        with pytest.raises(ValueError):
            await check_permission(request, None)
        return web.Response()

    app = web.Application()
    app.router.add_route('GET', '/', check)
    client = await aiohttp_client(app)
    resp = await client.get('/')
    assert 200 == resp.status
