import asyncio
import http.cookies

from aiohttp import hdrs, CIMultiDict

from .abc import AbstractIdentityPolicy


class CookiesIdentityPolicy(AbstractIdentityPolicy):

    def __init__(self):
        self._cookie_name = 'AIOHTTP_SECURITY'
        self._max_age = 30 * 24 * 3600

    @asyncio.coroutine
    def identify(self, request):
        identity = request.cookies.get(self._cookie_name)
        return identity

    @asyncio.coroutine
    def remember(self, request, identity, **kwargs):
        cookies = http.cookies.SimpleCookie()
        max_age = kwargs.pop('max_age', self._max_age)
        cookies[self._cookie_name] = identity
        cookie = cookies[self._cookie_name]
        cookie['max-age'] = max_age
        cookie.update(kwargs)

        value = cookie.output(header='')[1:]
        result = CIMultiDict({hdrs.SET_COOKIE: value})
        return result

    @asyncio.coroutine
    def forget(self, request):
        cookies = http.cookies.SimpleCookie()
        cookies[self._cookie_name] = ''
        cookie = cookies[self._cookie_name]
        value = cookie.output(header='')[1:]
        result = CIMultiDict({hdrs.SET_COOKIE: value})
        return result
