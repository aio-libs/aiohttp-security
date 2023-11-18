from aiohttp import web

from aiohttp_security import forget, remember


async def test_remember(aiohttp_client):

    async def do_remember(request):
        response = web.Response()
        await remember(request, response, 'Andrew')

    app = web.Application()
    app.router.add_route('POST', '/', do_remember)
    client = await aiohttp_client(app)
    resp = await client.post('/')
    assert 500 == resp.status
    exp = "Security subsystem is not initialized, call aiohttp_security.setup(...) first"
    assert exp == resp.reason


async def test_forget(aiohttp_client):

    async def do_forget(request):
        response = web.Response()
        await forget(request, response)

    app = web.Application()
    app.router.add_route('POST', '/', do_forget)
    client = await aiohttp_client(app)
    resp = await client.post('/')
    assert 500 == resp.status
    exp = "Security subsystem is not initialized, call aiohttp_security.setup(...) first"
    assert exp == resp.reason
