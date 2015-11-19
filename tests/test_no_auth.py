import asyncio
import pytest

from aiohttp import web
from aiohttp_security import authorized_userid, permits


@pytest.mark.run_loop
def test_authorized_userid(create_app_and_client):

    @asyncio.coroutine
    def check(request):
        userid = yield from authorized_userid(request)
        assert userid is None
        return web.Response()

    app, client = yield from create_app_and_client()
    app.router.add_route('GET', '/', check)
    resp = yield from client.get('/')
    assert 200 == resp.status
    yield from resp.release()


@pytest.mark.run_loop
def test_permits(create_app_and_client):

    @asyncio.coroutine
    def check(request):
        ret = yield from permits(request, 'read')
        assert ret
        ret = yield from permits(request, 'write')
        assert ret
        ret = yield from permits(request, 'unknown')
        assert ret
        return web.Response()

    app, client = yield from create_app_and_client()
    app.router.add_route('GET', '/', check)
    resp = yield from client.get('/')
    assert 200 == resp.status
    yield from resp.release()
