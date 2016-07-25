import asyncio

import sqlalchemy as sa

from aiohttp_security.abc import AbstractAuthorizationPolicy

from . import db


class DBAuthorizationPolicy(AbstractAuthorizationPolicy):
    def __init__(self, dbengine):
        self.dbengine = dbengine

    @asyncio.coroutine
    def authorized_userid(self, identity):
        with (yield from self.dbengine) as conn:
            where = sa.and_(db.users.c.login == identity,
                            sa.not_(db.users.c.disabled))
            query = db.users.count().where(where)
            ret = yield from conn.scalar(query)
            if ret:
                return identity
            else:
                return None

    @asyncio.coroutine
    def permits(self, identity, permission, context=None):
        if identity is None:
            return False

        with (yield from self.dbengine) as conn:
            where = sa.and_(db.users.c.login == identity,
                            sa.not_(db.users.c.disabled))
            query = db.users.select().where(where)
            ret = yield from conn.execute(query)
            user = yield from ret.fetchone()
            if user is not None:
                user_id = user[0]
                is_superuser = user[3]
                if is_superuser:
                    return True

                where = db.permissions.c.user_id == user_id
                query = db.permissions.select().where(where)
                ret = yield from conn.execute(query)
                result = yield from ret.fetchall()
                if ret is not None:
                    for record in result:
                        if record.perm_name == permission:
                            return True

            return False
