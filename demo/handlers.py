import asyncio
import functools

from aiohttp import web


from aiohttp_security import remember, forbid, authorized_user_id, permits


def require(permission):
    def wrapper(f):
        @asyncio.coroutine
        @functools.wraps(f)
        def wrapped(self, request):
            has_perm = yield from permits(request)
            if not has_perm:
                raise web.HTTPForbidden()
            return (yield from f(self, request))
        return wrapped
    return wrapper


class Web:
    @require('public')
    @asyncio.coroutine
    def index(self, request):
        pass

    @require('public')
    @asyncio.coroutine
    def login(self, request):
        pass

    @require('protected')
    @asyncio.coroutine
    def logout(self, request):
        pass

    @require('public')
    @asyncio.coroutine
    def public(self, request):
        pass

    @require('protected')
    @asyncio.coroutine
    def protected(self, request):
        pass
