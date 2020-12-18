from textwrap import dedent
from typing import Dict, NoReturn

from aiohttp import web

from aiohttp_security import (
    remember, forget, authorized_userid,
    check_permission, check_authorized,
)

from .authz import check_credentials
from .users import User


index_template = dedent("""
    <!doctype html>
        <head></head>
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


async def index(request: web.Request) -> web.Response:
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


async def login(request: web.Request) -> NoReturn:
    user_map: Dict[str, User] = request.app['user_map']
    invalid_response = web.HTTPUnauthorized(body='Invalid username / password combination')
    form = await request.post()
    username = form.get('username')
    password = form.get('password')

    if not (isinstance(username, str) and isinstance(password, str)):
        raise invalid_response

    verified = await check_credentials(user_map, username, password)
    if verified:
        response = web.HTTPFound('/')
        await remember(request, response, username)
        raise response

    raise invalid_response


async def logout(request: web.Request) -> web.Response:
    await check_authorized(request)
    response = web.Response(
        text='You have been logged out',
        content_type='text/html',
    )
    await forget(request, response)
    return response


async def internal_page(request: web.Request) -> web.Response:
    await check_permission(request, 'public')
    response = web.Response(
        text='This page is visible for all registered users',
        content_type='text/html',
    )
    return response


async def protected_page(request: web.Request) -> web.Response:
    await check_permission(request, 'protected')
    response = web.Response(
        text='You are on protected page',
        content_type='text/html',
    )
    return response


def configure_handlers(app: web.Application) -> None:
    router = app.router
    router.add_get('/', index, name='index')
    router.add_post('/login', login, name='login')
    router.add_get('/logout', logout, name='logout')
    router.add_get('/public', internal_page, name='public')
    router.add_get('/protected', protected_page, name='protected')
