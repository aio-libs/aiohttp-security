.. _aiohttp-security-usage:


=======
 Usage
=======

.. currentmodule:: aiohttp_security
.. highlight:: python


First of all, what is *aiohttp_security* about?

*aiohttp-security* is a set of public API functions as well as a
reference standard for implementation details for securing access to
assets served by a wsgi server.

Assets are secured using authentication and authorization as explained
below.  *aiohttp-security* is part of the
`aio-libs <https://github.com/aio-libs>`_ project which takes advantage
of asynchronous processing using Python's asyncio library.


Public API
==========

The API is agnostic to the low level implementation details such that
all client code only needs to implement the endpoints as provided by
the API (instead of calling policy code directly (see explanation
below)).

Via the API an application can:

(i) remember a user in a local session (:func:`remember`),
(ii) forget a user in a local session (:func:`forget`),
(iii) retrieve the :term:`userid` (:func:`authorized_userid`) of a
      remembered user from an :term:`identity` (discussed below), and
(iv) check the :term:`permission` of a remembered user (:func:`permits`).

The library internals are built on top of two concepts:

1) :term:`authentication`, and
2) :term:`authorization`.

There are  abstract base  classes for  both types  as well  as several
pre-built implementations that are  shipped with the library. However,
the end user is free to build their own implementations.

The library comes with two pre-built identity policies; one that uses
cookies, and one that uses sessions [#f1]_.  It is envisioned that in
most use cases developers will use one of the provided identity
policies (Cookie or Session) and implement their own authorization
policy.

The workflow is as follows:

1) User is authenticated.  This has to be implemented by the developer.
2) Once user is authenticated an identity string has to be created for
   that user.  This has to be implemented by the developer.
3) The identity string is passed to the Identity Policy's remember
   method and the user is now remembered (Cookie or Session if using
   built-in).  *Only once a user is remembered can the other API
   methods:* :func:`permits`, :func:`forget`, *and*
   :func:`authorized_userid` *be invoked* .
4) If the user tries to access a restricted asset the :func:`permits`
   method is called.  Usually assets are protected using the
   :func:`check_permission` helper.  This should return True if
   permission is granted.

The :func:`permits` method is implemented by the developer as part of
the :class:`AbstractAuthorizationPolicy` and passed to the
application at runtime via setup.

In addition a :func:`check_authorized` also
exists that requires no permissions (i.e. doesn't call :func:`permits`
method) but only requires that the user is remembered
(i.e. authenticated/logged in).




Authentication
==============

Authentication is the process where a user's identity is verified. It
confirms who the user is. This is traditionally done using a user name
and password (note: this is not the only way).

A authenticated user has no access rights, rather an authenticated
user merely confirms that the user exists and that the user is who
they say they are.

In *aiohttp_security* the developer is responsible for their own
authentication mechanism.  *aiohttp_security* only requires that the
authentication result in a identity string which corresponds to a
user's id in the underlying system.

.. note::

   :term:`identity` is a string that is shared between the browser and
   the server.  Therefore it is recommended that a random string
   such as a uuid or hash is used rather than things like a
   database primary key, user login/email, etc.

Identity Policy
===============

Once a user is authenticated the *aiohttp_security* API is invoked for
storing, retrieving, and removing a user's :term:`identity`.  This is
accommplished via AbstractIdentityPolicy's :func:`remember`,
:func:`identify`, and :func:`forget` methods.  The Identity Policy is
therefore the mechanism by which a authenticated user is persisted in
the system.

*aiohttp_security* has two built in identity policy's for this
purpose.  :class:`CookiesIdentityPolicy` that uses cookies and
:class:`SessionIdentityPolicy` that uses sessions via
``aiohttp-session`` library.

Authorization
==============

Once a user is authenticated (see above) it means that the user has an
:term:`identity`.  This :term:`identity` can now be used for checking
access rights or :term:`permission` using a :term:`authorization`
policy.

The authorization policy's :func:`permits()` method is used for this purpose.


When :class:`aiohttp.web.Request` has an :term:`identity` it means the
user has been authenticated and therefore has an :term:`identity` that
can be checked by the :term:`authorization` policy.

As noted above, :term:`identity` is a string that is shared between
the browser and the server.  Therefore it is recommended that a
random string such as a uuid or hash is used rather than things like
a database primary key, user login/email, etc.


.. rubric:: Footnotes
.. [#f1] jwt - json web tokens in the works
