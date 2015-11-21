import asyncio
import sqlalchemy as sa

from aiohttp_security.authorization import AbstractAuthorizationPolicy

from . import db


class DBAuthorizationPolicy(AbstractAuthorizationPolicy):
    def __init__(self, db_pool):
        self.db_pool = db_pool

    @asyncio.coroutine
    def authorized_user_id(self, identity):
        with (yield from self.db_pool) as conn:
            where = [db.users.c.login == identity,
                     not db.users.c.disabled]
            query = db.users.count().where(sa.and_(*where))
            ret = yield from conn.scalar(query)
            if ret:
                return identity
            else:
                return None

    @asyncio.coroutine
    def permits(self, identity, permission, context=None):
        with (yield from self.db_pool) as conn:
            where = [db.users.c.login == identity,
                     not db.users.c.disabled]
        record = self.data.get(identity)
        if record is not None:
            # TODO: implement actual permission checker
            if permission in record:
                return True
        return False
