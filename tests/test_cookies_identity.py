import asyncio
import socket
import unittest

import aiohttp
from aiohttp import web
from aiohttp_security import (remember, setup, forget,
                              AbstractAuthorizationPolicy)
from aiohttp_security.cookies_identity import CookiesIdentityPolicy
from aiohttp_security.api import IDENTITY_KEY


class Autz(AbstractAuthorizationPolicy):

    @asyncio.coroutine
    def permits(self, identity, permission, context=None):
        pass

    @asyncio.coroutine
    def authorized_userid(self, identity):
        pass


class TestCookiesIdentity(unittest.TestCase):

    def setUp(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(None)
        self.client = aiohttp.ClientSession(loop=self.loop)

    def tearDown(self):
        self.client.close()
        self.loop.run_until_complete(self.handler.finish_connections())
        self.srv.close()
        self.loop.run_until_complete(self.srv.wait_closed())
        self.loop.close()

    def find_unused_port(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('127.0.0.1', 0))
        port = s.getsockname()[1]
        s.close()
        return port

    @asyncio.coroutine
    def create_server(self):
        app = web.Application(loop=self.loop)
        setup(app, CookiesIdentityPolicy(), Autz())

        port = self.find_unused_port()
        self.handler = app.make_handler(
            debug=False, keep_alive_on=False)
        srv = yield from self.loop.create_server(
            self.handler, '127.0.0.1', port)
        url = "http://127.0.0.1:{}".format(port)
        self.srv = srv
        return app, srv, url

    def test_remember(self):

        @asyncio.coroutine
        def handler(request):
            response = web.Response()
            yield from remember(request, response, 'Andrew')
            return response

        @asyncio.coroutine
        def go():
            app, srv, url = yield from self.create_server()
            app.router.add_route('GET', '/', handler)
            resp = yield from self.client.get(url+'/')
            self.assertEqual(200, resp.status)
            self.assertEqual('Andrew',
                             self.client.cookies['AIOHTTP_SECURITY'].value)
            yield from resp.release()

        self.loop.run_until_complete(go())

    def test_identify(self):

        @asyncio.coroutine
        def create(request):
            response = web.Response()
            yield from remember(request, response, 'Andrew')
            return response

        @asyncio.coroutine
        def check(request):
            policy = request.app[IDENTITY_KEY]
            user_id = yield from policy.identify(request)
            self.assertEqual('Andrew', user_id)
            return web.Response()

        @asyncio.coroutine
        def go():
            app, srv, url = yield from self.create_server()
            app.router.add_route('GET', '/', check)
            app.router.add_route('POST', '/', create)
            resp = yield from self.client.post(url+'/')
            self.assertEqual(200, resp.status)
            yield from resp.release()
            resp = yield from self.client.get(url+'/')
            self.assertEqual(200, resp.status)
            yield from resp.release()

        self.loop.run_until_complete(go())

    def test_forget(self):

        @asyncio.coroutine
        def index(request):
            return web.Response()

        @asyncio.coroutine
        def login(request):
            response = web.HTTPFound(location='/')
            yield from remember(request, response, 'Andrew')
            return response

        @asyncio.coroutine
        def logout(request):
            response = web.HTTPFound(location='/')
            yield from forget(request, response)
            return response

        @asyncio.coroutine
        def go():
            app, srv, url = yield from self.create_server()
            app.router.add_route('GET', '/', index)
            app.router.add_route('POST', '/login', login)
            app.router.add_route('POST', '/logout', logout)
            resp = yield from self.client.post(url+'/login')
            self.assertEqual(200, resp.status)
            self.assertEqual(url+'/', resp.url)
            self.assertEqual('Andrew',
                             self.client.cookies['AIOHTTP_SECURITY'].value)
            yield from resp.release()
            resp = yield from self.client.post(url+'/logout')
            self.assertEqual(200, resp.status)
            self.assertEqual(url+'/', resp.url)
            self.assertEqual('', self.client.cookies['AIOHTTP_SECURITY'].value)
            yield from resp.release()

        self.loop.run_until_complete(go())
