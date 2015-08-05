import asyncio
import socket
import unittest

import aiohttp
from aiohttp import web
from aiohttp_security import remember, forget


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

    def test_remember(self):

        @asyncio.coroutine
        def do_remember(request):
            response = web.Response()
            yield from remember(request, response, 'Andrew')

        @asyncio.coroutine
        def go():
            app, srv, url = yield from self.create_server()
            app.router.add_route('POST', '/', do_remember)
            resp = yield from self.client.post(url)
            self.assertEqual(500, resp.status)
            self.assertEqual(('Security subsystem is not initialized, '
                              'call aiohttp_security.setup(...) first'),
                             resp.reason)
            yield from resp.release()

        self.loop.run_until_complete(go())

    def test_forget(self):

        @asyncio.coroutine
        def do_forget(request):
            response = web.Response()
            yield from forget(request, response)

        @asyncio.coroutine
        def go():
            app, srv, url = yield from self.create_server()
            app.router.add_route('POST', '/', do_forget)
            resp = yield from self.client.post(url)
            self.assertEqual(500, resp.status)
            self.assertEqual(('Security subsystem is not initialized, '
                              'call aiohttp_security.setup(...) first'),
                             resp.reason)
            yield from resp.release()

        self.loop.run_until_complete(go())
