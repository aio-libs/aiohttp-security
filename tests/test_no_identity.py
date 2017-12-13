from aiohttp import web
from aiohttp_security import remember, forget


async def test_remember(loop, test_client):

    async def do_remember(request):
        response = web.Response()
        await remember(request, response, 'Andrew')

    app = web.Application(loop=loop)
    app.router.add_route('POST', '/', do_remember)
    client = await test_client(app)
    resp = await client.post('/')
    assert 500 == resp.status
    assert (('Security subsystem is not initialized, '
             'call aiohttp_security.setup(...) first') ==
            resp.reason)


async def test_forget(loop, test_client):

    async def do_forget(request):
        response = web.Response()
        await forget(request, response)

    app = web.Application(loop=loop)
    app.router.add_route('POST', '/', do_forget)
    client = await test_client(app)
    resp = await client.post('/')
    assert 500 == resp.status
    assert (('Security subsystem is not initialized, '
             'call aiohttp_security.setup(...) first') ==
            resp.reason)
