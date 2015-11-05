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

   :return: :class:`str` :term:`userid` or ``None`` for session
            without signed in user.


.. coroutine:: permits(request, permission, context=None)

   Check user's permission.

   Return ``True`` if user remembered in *request* has specified *permission*.

   Allowed permissions as well as *context* meaning are depends on
   :class:`AbstractAuthorizationPolicy` implementation.

   Actually it's a wrapper around
   :meth:`AbstractAuthorizationPolicy.permits` coroutine.

   The user should be registered by :coroutine:`remember` before the call.

   :param request: :class:`aiohttp.web.Request` object.

   :param permission: requested permission. May be :class:`str` or
                      more complex object -- see used
                      :class:`AbstractAuthorizationPolicy`
                      implementation.

   :param context: additional object may be passed into
                   :meth:`AbstractAuthorizationPolicy.permission`
                   coroutine.

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

*aiohttp_security* is built on top of two *abstract policies* --
 :class:`AbstractIdentityPolicy` and
 :class:`AbstractAuthorizationPolicy`.

The first one responds on remembering, retrieving and forgetting
:term:`identity` into some session storage, e.g. HTTP cookie or
authorization token.

The second is responsible to return persistent :term:`userid` for
session-wide :term:`identity` and check user's permissions.

Most likely sofware developer reuses one of pre-implemented *identity
policies* from *aiohttp_security* but build *authorization policy*
from scratch for every application/project.


Identification policy
---------------------

.. class:: AbstractIdentityPolicy

   .. coroutinemethod:: identify(request)

      Extract :term:`identity` from *request*.

      Abstract method, should be overriden by descendant.

      :param request: :class:`aiohttp.web.Request` object.

      :return: the claimed identity of the user associated request or
               ``None`` if no identity can be found associated with
               the request.

   .. coroutinemethod:: remember(request, response, identity, **kwargs)

      Remember *identity*.

      May use *request* for accessing required data and *response* for
      storing *identity* (e.g. updating HTTP response cookies).

      *kwargs* may be used by concrete implementation for passing
      additional data.

      Abstract method, should be overriden by descendant.

      :param request: :class:`aiohttp.web.Request` object.

      :param response: :class:`aiohttp.web.StreamResponse` object or
                       derivative.

      :param identity: :term:`identity` to store.

      :param kwargs: optional additional arguments. An individual
                     identity policy and its consumers can decide on
                     the composition and meaning of the parameter.


   .. coroutinemethod:: forget(request, response)

      Forget previously stored :term:`identity`.

      May use *request* for accessing required data and *response* for
      dropping *identity* (e.g. updating HTTP response cookies).

      Abstract method, should be overriden by descendant.

      :param request: :class:`aiohttp.web.Request` object.

      :param response: :class:`aiohttp.web.StreamResponse` object or
                       derivative.
