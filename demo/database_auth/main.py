import asyncio

from aiohttp import web
from aiohttp_session import SimpleCookieStorage, setup as setup_session
from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession, async_sessionmaker,
                                    create_async_engine)

from aiohttp_security import SessionIdentityPolicy
from aiohttp_security import setup as setup_security
from .db import Base, User, Permission
from .db_auth import DBAuthorizationPolicy
from .handlers import Web


async def init_db(db_engine: AsyncEngine, db_session: async_sessionmaker[AsyncSession]) -> None:
    """Initialise DB with sample data."""
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with db_session.begin() as sess:
        pw = "$5$rounds=535000$2kqN9fxCY6Xt5/pi$tVnh0xX87g/IsnOSuorZG608CZDFbWIWBr58ay6S4pD"
        sess.add(User(username="admin", password=pw, is_superuser=True))
        moderator = User(username="moderator", password=pw)
        user = User(username="user", password=pw)
        sess.add(moderator)
        sess.add(user)
    async with db_session.begin() as sess:
        sess.add(Permission(user_id=moderator.id, name="protected"))
        sess.add(Permission(user_id=moderator.id, name="public"))
        sess.add(Permission(user_id=user.id, name="public"))


async def init_app() -> web.Application:
    app = web.Application()

    db_engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    app["db_session"] = async_sessionmaker(db_engine, expire_on_commit=False)

    await init_db(db_engine, app["db_session"])

    setup_session(app, SimpleCookieStorage())
    setup_security(app, SessionIdentityPolicy(), DBAuthorizationPolicy(app["db_session"]))

    web_handlers = Web()
    web_handlers.configure(app)

    return app


if __name__ == "__main__":
    web.run_app(init_app())
