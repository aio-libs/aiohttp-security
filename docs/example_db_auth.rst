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
    https://pythonhosted.org/passlib/

Database
--------

Launch these sql scripts to init database and fill it with sample data:

``psql template1 < demo/sql/init_db.sql``

and then

``psql template1 < demo/sql/sample_data.sql``


You will have two tables for storing users and their permissions

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

and second table is permissions table:

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

In our example we will lookup database by user login and if present return
this identity::


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


For permission check we will fetch the user first, check if he is superuser
(all permissions are allowed), otherwise check if permission is explicitly set
for that user::

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
                is_superuser = user[4]
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


Setup
-----

Once we have all the code in place we can install it for our application::

    from aiohttp_session.redis_storage import RedisStorage
    from aiohttp_security import setup as setup_security
    from aiohttp_security import SessionIdentityPolicy
    from aiopg.sa import create_engine
    from aioredis import create_pool

    from .db_auth import DBAuthorizationPolicy


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
        return app


Now we have authorization and can decorate every other view with access rights
based on permissions. This simple decorator (for class-based handlers) will
help to do that::

    def require(permission):
        def wrapper(f):
            @asyncio.coroutine
            @functools.wraps(f)
            def wrapped(self, request):
                has_perm = yield from permits(request, permission)
                if not has_perm:
                    message = 'User has no permission {}'.format(permission)
                    raise web.HTTPForbidden(body=message.encode())
                return (yield from f(self, request))
            return wrapped
        return wrapper


For each view you need to protect just apply the decorator on it::

    class Web:
        @require('protected')
        @asyncio.coroutine
        def protected_page(self, request):
            response = web.Response(body=b'You are on protected page')
            return response


If someone will try to access this protected page he will see::

    403, User has no permission "protected"


The best part about it is that you can implement any logic you want until it
follows the API conventions.

Launch application
------------------

For working with passwords there is a good library passlib_. Once you've
created some users you want to check their credentials on login. Similar
function may do what you trying to accomplish::

    from passlib.hash import sha256_crypt

    @asyncio.coroutine
    def check_credentials(db_engine, username, password):
        with (yield from db_engine) as conn:
            where = sa.and_(db.users.c.login == username,
                            sa.not_(db.users.c.disabled))
            query = db.users.select().where(where)
            ret = yield from conn.execute(query)
            user = yield from ret.fetchone()
            if user is not None:
                hash = user[2]
                return sha256_crypt.verify(password, hash)
        return False


Final step is to launch your application::

    python demo/main.py


Try to login with admin/moderator/user accounts (with *password* password)
and access **/public** or **/protected** endpoints.
