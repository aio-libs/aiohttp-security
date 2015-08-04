import asyncio
import socket
import unittest

import aiohttp
from aiohttp import web
from aiohttp_security import (authorized_userid, permits)


class TestNoAuth(unittest.TestCase):

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

        port = self.find_unused_port()
        self.handler = app.make_handler(
            debug=False, keep_alive_on=False)
        srv = yield from self.loop.create_server(
            self.handler, '127.0.0.1', port)
        url = "http://127.0.0.1:{}/".format(port)
        self.srv = srv
        return app, srv, url

    def test_authorized_userid(self):

        @asyncio.coroutine
        def check(request):
            userid = yield from authorized_userid(request)
            self.assertIsNone(userid)
            return web.Response()

        @asyncio.coroutine
        def go():
            app, srv, url = yield from self.create_server()
            app.router.add_route('GET', '/', check)
            resp = yield from self.client.get(url)
            self.assertEqual(200, resp.status)
            yield from resp.release()

        self.loop.run_until_complete(go())

    def test_permits(self):

        @asyncio.coroutine
        def check(request):
            ret = yield from permits(request, 'read')
            self.assertTrue(ret)
            ret = yield from permits(request, 'write')
            self.assertTrue(ret)
            ret = yield from permits(request, 'unknown')
            self.assertTrue(ret)
            return web.Response()

        @asyncio.coroutine
        def go():
            app, srv, url = yield from self.create_server()
            app.router.add_route('GET', '/', check)
            resp = yield from self.client.get(url)
            self.assertEqual(200, resp.status)
            yield from resp.release()

        self.loop.run_until_complete(go())
