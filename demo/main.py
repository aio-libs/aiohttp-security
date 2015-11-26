import asyncio

from aiohttp import web
from aiohttp_session import setup as setup_session
from aiohttp_session.redis_storage import RedisStorage
from aiohttp_security import setup as setup_security
from aiohttp_security import SessionIdentityPolicy
from aiopg.sa import create_engine
from aioredis import create_pool


from demo.db_auth import DBAuthorizationPolicy


@asyncio.coroutine
def init(loop):
    redis_pool = yield from create_pool(('localhost', 6379))
    dbengine = yield from create_engine(user='aiohttp_security',
                                        password='aiohttp_security',
                                        database='aiohttp_security',
                                        host='127.0.0.1')
    app = web.Application(loop=loop)
    setup_session(app, RedisStorage(redis_pool))
    setup_security(app,
                   SessionIdentityPolicy(),
                   DBAuthorizationPolicy(dbengine))

    app.add_route()

    handler = app.make_handler()
    srv = yield from loop.create_server(handler, '127.0.0.1', 8080)
    print("Server started at http://127.0.0.1:8080")
    return srv, handler


@asyncio.coroutine
def finalize(loop, srv, handler):
    pass


loop = asyncio.get_event_loop()
srv, handler = loop.run_until_complete(init(loop))
try:
    loop.run_forever()
except KeyboardInterrupt:
    loop.run_until_complete((finalize(loop)))
