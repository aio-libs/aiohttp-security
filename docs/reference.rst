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

   Remember *identity* in *response*, e.g. by storing a cookie or
   saving info into session.

   The action is performed by registered
   :coroutinemethod:`AbstractIdentityPolicy.remember`.

   Usually the *idenity* is stored in user cookies homehow for using by
   :coroutine:`authorized_userid` and :coroutine:`permits`.

   :param request: :class:`aiohttp.web.Request` object.

   :param response: :class:`aiohttp.web.StreamResponse` and
                    descendants like :class:`aiohttp.web.Response`.

   :param str identity: :class:`aiohttp.web.Request` object.

   :param **kwargs: additional arguments passed to
                    :coroutinemethod:`AbstractIdentityPolicy.remember`.

                    They are policy-specific and may be used, e.g. for
                    specifiying cookie lifetime.

.. coroutine:: forget(request, response)

   Forget previously remembered :term:`identity`.

   The action is performed by registered
   :coroutinemethod:`AbstractIdentityPolicy.forget`.

   :param request: :class:`aiohttp.web.Request` object.

   :param response: :class:`aiohttp.web.StreamResponse` and
                    descendants like :class:`aiohttp.web.Response`.


.. coroutine:: authorized_userid(request)

   Retrieve :term:`userid`.

   The user should be registered by :coroutine:`remember` before the call.

   :param request: :class:`aiohttp.web.Request` object.

   :return: :class:`str` :term:`userid` or ``None`` for not signed in users.


.. coroutine:: permits(request, permission, context=None)

   :param request: :class:`aiohttp.web.Request` object.

   :return: ``True`` if registered user has requested *permission*,
            ``False`` otherwise.


.. function:: setup(app, identity_policy, autz_policy)

   Setup :mod:`aiohttp` application with security policies.

   :param app: aiohttp :class:`aiohttp.web.Application` instance.

   :param identity_policy: indentification policy, an
                           :class:`AbstractIdentityPolicy` instance.

   :param autz_policy: authorization policy, an
                           :class:`AbstractAuthorizationPolicy` instance.


Abstract policies
=================


