from enum import Enum

import sqlalchemy as sa
from passlib.hash import sha256_crypt
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload

from aiohttp_security.abc import AbstractAuthorizationPolicy
from .db import User


def _where_authorized(identity: str) -> tuple[sa.sql.ColumnElement[bool], ...]:
    return (User.username == identity, ~User.disabled)


class DBAuthorizationPolicy(AbstractAuthorizationPolicy):
    def __init__(self, dbsession: async_sessionmaker[AsyncSession]):
        self.dbsession = dbsession

    async def authorized_userid(self, identity: str) -> str | None:
        where = _where_authorized(identity)
        async with self.dbsession() as sess:
            user_id = await sess.scalar(sa.select(User.id).where(*where))
        return str(user_id) if user_id else None

    async def permits(self, identity: str | None, permission: str | Enum,
                      context: dict[str, object] | None = None) -> bool:
        if identity is None:
            return False

        where = _where_authorized(identity)
        stmt = sa.select(User).options(selectinload(User.permissions)).where(*where)
        async with self.dbsession() as sess:
            user = await sess.scalar(stmt)

        if user is None:
            return False
        if user.is_superuser:
            return True
        return any(p.name == permission for p in user.permissions)


async def check_credentials(db_session: async_sessionmaker[AsyncSession],
                            username: str, password: str) -> bool:
    where = _where_authorized(username)
    async with db_session() as sess:
        hashed_pw = await sess.scalar(sa.select(User.password).where(*where))

    if hashed_pw is None:
        return False

    return sha256_crypt.verify(password, hashed_pw)
