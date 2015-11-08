.. _aiohttp-security-usage:


=======
 Usage
=======

.. currentmodule:: aiohttp_security
.. highlight:: python

The library is build on top of two policies: :term:`authentication`
and :term:`authorization`.


Authentication
==============

Actions related to retrieving, storing and removing user's
:term:`identity`.

Authenticated user has no access rights, the system even has no
knowledge is there the user still registered in DB.

If :term:`request` has an :term:`identity` it means the user has
some ID that should be checked by :term:`authorization` policy.






identity is a string shared between browser and server.
Thus it's not supposed to be database primary key, user login/email etc.
Random string like uuid or hash is better choice.

