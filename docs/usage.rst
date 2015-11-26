.. _aiohttp-security-usage:


=======
 Usage
=======

.. currentmodule:: aiohttp_security
.. highlight:: python


First of all, what is *aiohttp_security* about?

It is a set of public API functions and standard for implementation details.

API is implementation agnostic, all client code should not call policy
code (see below) directly but use API only.

Via API application can remember/forget user in local session
(:func:`remember`/:func:`forget`), retrieve :term:`userid`
(:func:`authorized_userid`) and check :term:`permission` for
remembered user (:func:`permits`).

The library internals are built on top of two policies:
:term:`authentication` and :term:`authorization`. There are abstract
base classes for both concepts as well as several implementations
shipped with the library. End user is free to build own implemetations
if needed.

Public API
==========


Authentication
==============

Actions related to retrieving, storing and removing user's
:term:`identity`.

Authenticated user has no access rights, the system even has no
knowledge is there the user still registered in DB.

If :class:`aiohttp.web.Request` has an :term:`identity` it means the user has
some ID that should be checked by :term:`authorization` policy.






identity is a string shared between browser and server.
Thus it's not supposed to be database primary key, user login/email etc.
Random string like uuid or hash is better choice.
