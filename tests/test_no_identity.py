import asyncio
import pytest

from aiohttp import web
from aiohttp_security import remember, forget


@pytest.mark.run_loop
def test_remember(create_app_and_client):

    @asyncio.coroutine
    def do_remember(request):
        response = web.Response()
        yield from remember(request, response, 'Andrew')

    app, client = yield from create_app_and_client()
    app.router.add_route('POST', '/', do_remember)
    resp = yield from client.post('/')
    assert 500 == resp.status
    assert (('Security subsystem is not initialized, '
             'call aiohttp_security.setup(...) first') ==
            resp.reason)
    yield from resp.release()


@pytest.mark.run_loop
def test_forget(create_app_and_client):

    @asyncio.coroutine
    def do_forget(request):
        response = web.Response()
        yield from forget(request, response)

    app, client = yield from create_app_and_client()
    app.router.add_route('POST', '/', do_forget)
    resp = yield from client.post('/')
    assert 500 == resp.status
    assert (('Security subsystem is not initialized, '
             'call aiohttp_security.setup(...) first') ==
            resp.reason)
    yield from resp.release()
