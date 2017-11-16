from aiohttp import web
from aiohttp_jinja2 import render_template

from aiohttp_security import authorize, get_user_identity, remember, forget


@authorize(required=True, redirect_url='/login', permission='Steve')
async def index(request, identity=None):
    context = {'name': identity}
    response = render_template('index.html', request, context)
    return response


async def login(request):
    identity = await get_user_identity(request)
    if identity:
        return web.HTTPFound('/')
    response = render_template('login.html', request, {})
    return response


async def login_post(request):
    post_data = await request.post()
    user_id = post_data['username']
    password = post_data['password']
    response = web.Response(body=b'OK')
    await remember(request, response, user_id)
    return response


async def logout(request):
    response = web.Response(body=b'OK')
    await forget(request, response)
    return response
