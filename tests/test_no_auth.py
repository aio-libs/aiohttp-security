import asyncio

from aiohttp import web
from aiohttp_security import authorized_userid, permits


@asyncio.coroutine
def test_authorized_userid(loop, test_client):

    @asyncio.coroutine
    def check(request):
        userid = yield from authorized_userid(request)
        assert userid is None
        return web.Response()

    app = web.Application(loop=loop)
    app.router.add_route('GET', '/', check)
    client = yield from test_client(app)
    resp = yield from client.get('/')
    assert 200 == resp.status
    yield from resp.release()


@asyncio.coroutine
def test_permits(loop, test_client):

    @asyncio.coroutine
    def check(request):
        ret = yield from permits(request, 'read')
        assert ret
        ret = yield from permits(request, 'write')
        assert ret
        ret = yield from permits(request, 'unknown')
        assert ret
        return web.Response()

    app = web.Application(loop=loop)
    app.router.add_route('GET', '/', check)
    client = yield from test_client(app)
    resp = yield from client.get('/')
    assert 200 == resp.status
    yield from resp.release()
