import functools
from textwrap import dedent

from aiohttp import web

from aiohttp_security import remember, forget, authorized_userid, permits

from .authz import check_credentials


def require(permission):
    def wrapper(f):
        @functools.wraps(f)
        async def wrapped(request):
            has_perm = await permits(request, permission)
            if not has_perm:
                message = 'User has no permission {}'.format(permission)
                raise web.HTTPForbidden(body=message.encode())
            return await f(request)
        return wrapped
    return wrapper


index_template = dedent("""
    <!doctype html>
    <head>
    </head>
    <body>
    <p>{message}</p>
    <form action="/login" method="post">
      Login:
      <input type="text" name="username">
      Password:
      <input type="password" name="password">
      <input type="submit" value="Login">
    </form>
    <a href="/logout">Logout</a>
    </body>
    """)


async def index(request):
    username = await authorized_userid(request)
    if username:
        template = index_template.format(
            message='Hello, {username}!'.format(username=username))
    else:
        template = index_template.format(message='You need to login')
    return web.Response(
        text=template,
        content_type='text/html',
    )


async def login(request):
    response = web.HTTPFound('/')
    form = await request.post()
    username = form.get('username')
    password = form.get('password')

    verified = await check_credentials(request.app.user_map, username, password)
    if verified:
        await remember(request, response, username)
        return response

    return web.HTTPUnauthorized(body='Invalid username / password combination')


@require('public')
async def logout(request):
    response = web.Response(
        text='You have been logged out',
        content_type='text/html',
    )
    await forget(request, response)
    return response


@require('public')
async def internal_page(request):
    # pylint: disable=unused-argument
    response = web.Response(
        text='This page is visible for all registered users',
        content_type='text/html',
    )
    return response


@require('protected')
async def protected_page(request):
    # pylint: disable=unused-argument
    response = web.Response(
        text='You are on protected page',
        content_type='text/html',
    )
    return response


def configure_handlers(app):
    router = app.router
    router.add_get('/', index, name='index')
    router.add_post('/login', login, name='login')
    router.add_get('/logout', logout, name='logout')
    router.add_get('/public', internal_page, name='public')
    router.add_get('/protected', protected_page, name='protected')
