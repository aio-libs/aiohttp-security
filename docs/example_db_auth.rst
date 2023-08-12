.. _aiohttp-security-example-db-auth:

=======================================
Permissions with database-based storage
=======================================

We use :class:`~aiohttp_session.SimpleCookieStorage` and an in-memory SQLite DB to
make it easy to try out the demo. When developing an application, you should use
:class:`~aiohttp_session.cookie_storage.EncryptedCookieStorage` or
:class:`~aiohttp_session.redis_storage.RedisStorage` and a production-ready database.
If you want the full source code in advance or for comparison, check out
the `demo source`_.

.. _demo source:
    https://github.com/aio-libs/aiohttp_security/tree/master/demo

.. _passlib:
    https://passlib.readthedocs.io

Database
--------

When the application runs, we initialise the DB with sample data using SQLAlchemy
ORM:

.. literalinclude:: demo/database_auth/main.py
   :pyobject: init_db


This will consist of 2 tables/models created in ``db.py``:

Users:

.. literalinclude:: demo/database_auth/db.py
   :pyobject: User

And their permissions:

.. literalinclude:: demo/database_auth/db.py
   :pyobject: Permission


Writing policies
----------------

You need to implement two entities:
:class:`IdentityPolicy<aiohttp_security.AbstractIdentityPolicy>` and
:class:`AuthorizationPolicy<aiohttp_security.AbstractAuthorizationPolicy>`.
First one should have these methods:
:class:`~aiohttp_security.AbstractIdentityPolicy.identify`,
:class:`~aiohttp_security.AbstractIdentityPolicy.remember` and
:class:`~aiohttp_security.AbstractIdentityPolicy.forget`.
For the second one:
:class:`~aiohttp_security.AbstractAuthorizationPolicy.authorized_userid` and
:class:`~aiohttp_security.AbstractAuthorizationPolicy.permits`. We will use the
included :class:`~aiohttp_security.SessionIdentityPolicy` and write our own
database-based authorization policy.

In our example we will lookup a user login in the database and, if present, return
the identity.

.. literalinclude:: demo/database_auth/db_auth.py
   :pyobject: DBAuthorizationPolicy.authorized_userid


For permission checking, we will fetch the user first, check if he is superuser
(all permissions are allowed), otherwise check if the permission is explicitly set
for that user.

.. literalinclude:: demo/database_auth/db_auth.py
   :pyobject: DBAuthorizationPolicy.permits


Setup
-----

Once we have all the code in place we can install it for our application:

.. literalinclude:: demo/database_auth/main.py
   :pyobject: init_app

Now we have authorization and can decorate every other view with access rights
based on permissions. There are two helpers included for this::

    from aiohttp_security import check_authorized, check_permission

For each view you need to protect - just apply the decorator on it.

.. literalinclude:: demo/database_auth/handlers.py
   :pyobject: Web.protected_page

or

.. literalinclude:: demo/database_auth/handlers.py
   :pyobject: Web.logout

If someone tries to access that protected page he will see::

    403: Forbidden


The best part of it - you can implement any logic you want following the API conventions.

Launch application
------------------

For working with passwords there is a good library passlib_. Once you've
created some users you want to check their credentials on login. A similar
function may do what you are trying to accomplish::

    from passlib.hash import sha256_crypt

.. literalinclude:: demo/database_auth/db_auth.py
   :pyobject: check_credentials


Final step is to launch your application::

    python -m database_auth


Try to login with admin/moderator/user accounts (with **password** password)
and access **/public** or **/protected** endpoints.
