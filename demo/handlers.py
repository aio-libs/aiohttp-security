import asyncio

from aiohttp import web

from aiohttp_security import (
    authorized_userid,
    forget,
    login_required,
    remember,
)

from .db_auth import check_credentials


class Web(object):
    index_template = """
<!doctype html>
<head>
</head>
<body>
<p>{message}</p>
<form action="/login" method="post">
  Login:
  <input type="text" name="login">
  Password:
  <input type="password" name="password">
  <input type="submit" value="Login">
</form>
<a href="/logout">Logout</a>
</body>
"""

    @asyncio.coroutine
    def index(self, request):
        username = yield from authorized_userid(request)
        if username:
            template = self.index_template.format(
                message='Hello, {username}!'.format(username=username))
        else:
            template = self.index_template.format(message='You need to login')
        response = web.Response(body=template.encode())
        return response

    @asyncio.coroutine
    def login(self, request):
        response = web.HTTPFound('/')
        form = yield from request.post()
        login = form.get('login')
        password = form.get('password')
        db_engine = request.app.db_engine
        if (yield from check_credentials(db_engine, login, password)):
            yield from remember(request, response, login)
            return response

        return web.HTTPUnauthorized(
            body=b'Invalid username/password combination')

    @login_required('public')
    @asyncio.coroutine
    def logout(self, request):
        response = web.Response(body=b'You have been logged out')
        yield from forget(request, response)
        return response

    @login_required('public')
    @asyncio.coroutine
    def internal_page(self, request):
        response = web.Response(
            body=b'This page is visible for all registered users')
        return response

    @login_required('protected')
    @asyncio.coroutine
    def protected_page(self, request):
        response = web.Response(body=b'You are on protected page')
        return response

    def configure(self, app):
        router = app.router
        router.add_route('GET', '/', self.index, name='index')
        router.add_route('POST', '/login', self.login, name='login')
        router.add_route('GET', '/logout', self.logout, name='logout')
        router.add_route('GET', '/public', self.internal_page, name='public')
        router.add_route('GET', '/protected', self.protected_page,
                         name='protected')
