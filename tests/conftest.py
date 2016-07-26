import gc
import socket
import asyncio

import pytest
import aiohttp

from aiohttp import web


@pytest.fixture
def unused_port():
    def f():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', 0))
            return s.getsockname()[1]
    return f


@pytest.yield_fixture
def loop(request):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(None)

    yield loop

    loop.stop()
    loop.run_forever()
    loop.close()
    gc.collect()
    asyncio.set_event_loop(None)


@pytest.yield_fixture
def create_server(loop, unused_port):
    app = handler = srv = None

    @asyncio.coroutine
    def create(*, debug=False, ssl_ctx=None, proto='http'):
        nonlocal app, handler, srv
        app = web.Application(loop=loop)
        port = unused_port()
        handler = app.make_handler(debug=debug, keep_alive_on=False)
        srv = yield from loop.create_server(handler, '127.0.0.1', port,
                                            ssl=ssl_ctx)
        if ssl_ctx:
            proto += 's'
        url = "{}://127.0.0.1:{}".format(proto, port)
        return app, url

    yield create

    @asyncio.coroutine
    def finish():
        if handler is not None:
            yield from handler.finish_connections()
        if app is not None:
            yield from app.finish()
        if srv is not None:
            srv.close()
            yield from srv.wait_closed()

    loop.run_until_complete(finish())


class Client:
    def __init__(self, session, url):
        self._session = session
        if not url.endswith('/'):
            url += '/'
        self._url = url

    @property
    def cookies(self):
        return self._session.cookies

    def close(self):
        self._session.close()

    def get(self, path, **kwargs):
        while path.startswith('/'):
            path = path[1:]
        url = self._url + path
        resp = self._session.get(url, **kwargs)
        return resp

    def post(self, path, **kwargs):
        while path.startswith('/'):
            path = path[1:]
        url = self._url + path
        return self._session.post(url, **kwargs)

    def ws_connect(self, path, **kwargs):
        while path.startswith('/'):
            path = path[1:]
        url = self._url + path
        return self._session.ws_connect(url, **kwargs)


@pytest.yield_fixture
def create_app_and_client(create_server, loop):
    client = None
    cookie_jar = aiohttp.CookieJar(loop=loop, unsafe=True)

    @asyncio.coroutine
    def maker(*, server_params=None, client_params=None):
        nonlocal client
        if server_params is None:
            server_params = {}
        server_params.setdefault('debug', False)
        server_params.setdefault('ssl_ctx', None)
        app, url = yield from create_server(**server_params)
        if client_params is None:
            client_params = {}

        client = Client(
            aiohttp.ClientSession(loop=loop, cookie_jar=cookie_jar),
            url
        )
        return app, client

    yield maker
    if client is not None:
        client.close()


@pytest.mark.tryfirst
def pytest_pycollect_makeitem(collector, name, obj):
    if collector.funcnamefilter(name):
        if not callable(obj):
            return
        item = pytest.Function(name, parent=collector)
        if 'run_loop' in item.keywords:
            return list(collector._genfunctions(name, obj))


@pytest.mark.tryfirst
def pytest_pyfunc_call(pyfuncitem):
    """
    Run asyncio marked test functions in an event loop instead of a normal
    function call.
    """
    if 'run_loop' in pyfuncitem.keywords:
        funcargs = pyfuncitem.funcargs
        loop = funcargs['loop']
        testargs = {arg: funcargs[arg]
                    for arg in pyfuncitem._fixtureinfo.argnames}
        loop.run_until_complete(pyfuncitem.obj(**testargs))
        return True


def pytest_runtest_setup(item):
    if 'run_loop' in item.keywords and 'loop' not in item.fixturenames:
        # inject an event loop fixture for all async tests
        item.fixturenames.append('loop')
