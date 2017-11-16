import asyncio
import os

import jinja2
from aiohttp import web
from aiohttp_jinja2 import setup as setup_jinja
from aiohttp_session import setup as setup_session
from aiohttp_session.redis_storage import RedisStorage
from aioredis import create_pool

from aiohttp_security import setup as setup_security, SessionIdentityPolicy
from .auth_policy import StubAuthorizationPolicy
from .handlers import index, login, login_post, logout

loop = asyncio.get_event_loop()
redis_pool = loop.run_until_complete(create_pool(('localhost', 6379)))
app = web.Application(loop=loop)
setup_session(app, RedisStorage(redis_pool))
setup_security(app,
               SessionIdentityPolicy(),
               StubAuthorizationPolicy())
setup_jinja(app, loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))
app.router.add_route('GET', '/', index)
app.router.add_route('GET', '/login', login)
app.router.add_route('POST', '/login', login_post)
app.router.add_route('GET', '/logout', logout)
web.run_app(app)
