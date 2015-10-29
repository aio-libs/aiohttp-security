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

   Remember identity into response.

   The action is performed by registered
   :coroutinemethod:`AbstractIdentityPolicy.remember`.

   Usually the *idenity* is stored in user cookies homehow for using by
   :coroutine:`authorized_userid` and :coroutine:`permits`.

   :param request: :class:`aiohttp.web.Request` object.

   :param response: :class:`aiohttp.web.StreamResponse` and
                    descendants like :class:`aiohttp.web.Response`.

   :param str identity: :class:`aiohttp.web.Request` object.

.. function:: setup(app, identity_policy, autz_policy)

   Setup :mod:`aiohttp` application with security policies.

   :param app: aiohttp :class:`aiohttp.web.Application` instance.

   :param identity_policy: indentification policy, an
                           :class:`AbstractIdentityPolicy` instance.

   :param autz_policy: authorization policy, an
                           :class:`AbstractAuthorizationPolicy` instance.


Abstract policies
=================


