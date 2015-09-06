.. _aiohttp-security-reference:


===========
 Reference
===========

.. module:: aiohttp_security
.. currentmodule:: aiohttp_security
.. highlight:: python


Public API functions
====================

.. coroutine:: remember(request, response, identity, **kwargs)

   Remember identity


.. function:: setup(app, identity_policy, autz_policy)

   Setup :mod:`aiohttp` application with security policies.


Abstract policies
=================


