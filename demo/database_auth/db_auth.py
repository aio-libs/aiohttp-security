from enum import Enum
from typing import Any, Optional, Union

import sqlalchemy as sa
from passlib.hash import sha256_crypt

from aiohttp_security.abc import AbstractAuthorizationPolicy
from . import db


class DBAuthorizationPolicy(AbstractAuthorizationPolicy):
    def __init__(self, dbengine: Any):
        self.dbengine = dbengine

    async def authorized_userid(self, identity: str) -> Optional[str]:
        async with self.dbengine.acquire() as conn:
            where = sa.and_(db.users.c.login == identity,
                            sa.not_(db.users.c.disabled))  # type: ignore[no-untyped-call]
            query = db.users.count().where(where)
            ret = await conn.scalar(query)
            if ret:
                return identity
            else:
                return None

    async def permits(self, identity: str, permission: Union[str, Enum],
                      context: None = None) -> bool:
        async with self.dbengine.acquire() as conn:
            where = sa.and_(db.users.c.login == identity,
                            sa.not_(db.users.c.disabled))  # type: ignore[no-untyped-call]
            query = db.users.select().where(where)
            ret = await conn.execute(query)
            user = await ret.fetchone()
            if user is not None:
                user_id = user[0]
                is_superuser = user[3]
                if is_superuser:
                    return True

                where = db.permissions.c.user_id == user_id
                query = db.permissions.select().where(where)
                ret = await conn.execute(query)
                result = await ret.fetchall()
                if ret is not None:
                    for record in result:
                        if record.perm_name == permission:
                            return True

            return False


async def check_credentials(db_engine: Any, username: str, password: str) -> bool:
    async with db_engine.acquire() as conn:
        where = sa.and_(db.users.c.login == username,
                        sa.not_(db.users.c.disabled))  # type: ignore[no-untyped-call]
        query = db.users.select().where(where)
        ret = await conn.execute(query)
        user = await ret.fetchone()
        if user is not None:
            hashed = user[2]
            return sha256_crypt.verify(password, hashed)  # type: ignore[no-any-return]
    return False
