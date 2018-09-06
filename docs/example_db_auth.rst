.. _aiohttp-security-example-db-auth:

===========================================
Permissions with PostgreSQL-based storage
===========================================

Make sure that you have PostgreSQL and Redis servers up and running.
If you want the full source code in advance or for comparison, check out
the `demo source`_.

.. _demo source:
    https://github.com/aio-libs/aiohttp_security/tree/master/demo

.. _passlib:
    https://passlib.readthedocs.io

Database
--------

Launch these sql scripts to init database and fill it with sample data:

``psql template1 < demo/sql/init_db.sql``

and

``psql template1 < demo/sql/sample_data.sql``


Now you have two tables:

- for storing users

+--------------+
| users        |
+==============+
| id           |
+--------------+
| login        |
+--------------+
| passwd       |
+--------------+
| is_superuser |
+--------------+
| disabled     |
+--------------+

- for storing their permissions

+-----------------+
| permissions     |
+=================+
| id              |
+-----------------+
| user_id         |
+-----------------+
| permission_name |
+-----------------+


Writing policies
----------------

You need to implement two entities: *IdentityPolicy* and *AuthorizationPolicy*.
First one should have these methods: *identify*, *remember* and *forget*.
For second one: *authorized_userid* and *permits*. We will use built-in
*SessionIdentityPolicy* and write our own database-based authorization policy.

In our example we will lookup database by user login and if presents then return
this identity::


    async def authorized_userid(self, identity):
        async with self.dbengine as conn:
            where = sa.and_(db.users.c.login == identity,
                            sa.not_(db.users.c.disabled))
            query = db.users.count().where(where)
            ret = await conn.scalar(query)
            if ret:
                return identity
            else:
                return None


For permission checking we will fetch the user first, check if he is superuser
(all permissions are allowed), otherwise check if permission is explicitly set
for that user::

    async def permits(self, identity, permission, context=None):
        if identity is None:
            return False

        async with self.dbengine as conn:
            where = sa.and_(db.users.c.login == identity,
                            sa.not_(db.users.c.disabled))
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


Setup
-----

Once we have all the code in place we can install it for our application::

    from aiohttp_session.redis_storage import RedisStorage
    from aiohttp_security import setup as setup_security
    from aiohttp_security import SessionIdentityPolicy
    from aiopg.sa import create_engine
    from aioredis import create_pool

    from .db_auth import DBAuthorizationPolicy


    async def init(loop):
        redis_pool = await create_pool(('localhost', 6379))
        dbengine = await create_engine(user='aiohttp_security',
                                       password='aiohttp_security',
                                       database='aiohttp_security',
                                       host='127.0.0.1')
        app = web.Application()
        setup_session(app, RedisStorage(redis_pool))
        setup_security(app,
                       SessionIdentityPolicy(),
                       DBAuthorizationPolicy(dbengine))
        return app


Now we have authorization and can decorate every other view with access rights
based on permissions. There are already implemented two helpers::

    from aiohttp_security import check_authorized, check_permission

For each view you need to protect - just apply the decorator on it::

    class Web:
        async def protected_page(self, request):
            await check_permission(request, 'protected')
            response = web.Response(body=b'You are on protected page')
            return response

or::

    class Web:
        async def logout(self, request):
            await check_authorized(request)
            response = web.Response(body=b'You have been logged out')
            await forget(request, response)
            return response

If someone try to access that protected page he will see::

    403: Forbidden


The best part of it - you can implement any logic you want until it
follows the API conventions.

Launch application
------------------

For working with passwords there is a good library passlib_. Once you've
created some users you want to check their credentials on login. Similar
function may do what you are trying to accomplish::

    from passlib.hash import sha256_crypt

    async def check_credentials(db_engine, username, password):
        async with  db_engine as conn:
            where = sa.and_(db.users.c.login == username,
                            sa.not_(db.users.c.disabled))
            query = db.users.select().where(where)
            ret = await conn.execute(query)
            user = await ret.fetchone()
            if user is not None:
                hash = user[2]
                return sha256_crypt.verify(password, hash)
        return False


Final step is to launch your application::

    python demo/database_auth/main.py


Try to login with admin/moderator/user accounts (with **password** password)
and access **/public** or **/protected** endpoints.
