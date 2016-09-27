import asyncio

from aiohttp import web
from aiohttp_security import remember, forget


@asyncio.coroutine
def test_remember(loop, test_client):

    @asyncio.coroutine
    def do_remember(request):
        response = web.Response()
        yield from remember(request, response, 'Andrew')

    app = web.Application(loop=loop)
    app.router.add_route('POST', '/', do_remember)
    client = yield from test_client(app)
    resp = yield from client.post('/')
    assert 500 == resp.status
    assert (('Security subsystem is not initialized, '
             'call aiohttp_security.setup(...) first') ==
            resp.reason)
    yield from resp.release()


@asyncio.coroutine
def test_forget(loop, test_client):

    @asyncio.coroutine
    def do_forget(request):
        response = web.Response()
        yield from forget(request, response)

    app = web.Application(loop=loop)
    app.router.add_route('POST', '/', do_forget)
    client = yield from test_client(app)
    resp = yield from client.post('/')
    assert 500 == resp.status
    assert (('Security subsystem is not initialized, '
             'call aiohttp_security.setup(...) first') ==
            resp.reason)
    yield from resp.release()
