.. _aiohttp-security-reference:


===========
 Reference
===========

.. module:: aiohttp_security
.. currentmodule:: aiohttp_security
.. highlight:: python


Public API functions
====================

.. function:: setup(app, identity_policy, autz_policy)

   Setup :mod:`aiohttp` application with security policies.

   :param app: aiohttp :class:`aiohttp.web.Application` instance.

   :param identity_policy: indentification policy, an
                           :class:`AbstractIdentityPolicy` instance.

   :param autz_policy: authorization policy, an
                           :class:`AbstractAuthorizationPolicy` instance.


.. coroutinefunction:: remember(request, response, identity, **kwargs)

   Remember *identity* in *response*, e.g. by storing a cookie or
   saving info into session.

   The action is performed by registered
   :meth:`AbstractIdentityPolicy.remember`.

   Usually the *identity* is stored in user cookies somehow for using by
   :func:`authorized_userid` and :func:`permits`.

   :param request: :class:`aiohttp.web.Request` object.

   :param response: :class:`aiohttp.web.StreamResponse` and
                    descendants like :class:`aiohttp.web.Response`.

   :param str identity: :class:`aiohttp.web.Request` object.

   :param kwargs: additional arguments passed to
                  :meth:`AbstractIdentityPolicy.remember`.

                  They are policy-specific and may be used, e.g. for
                  specifiying cookie lifetime.

.. coroutinefunction:: forget(request, response)

   Forget previously remembered :term:`identity`.

   The action is performed by registered
   :meth:`AbstractIdentityPolicy.forget`.

   :param request: :class:`aiohttp.web.Request` object.

   :param response: :class:`aiohttp.web.StreamResponse` and
                    descendants like :class:`aiohttp.web.Response`.


.. coroutinefunction:: check_authorized(request)

   Checker that doesn't pass if user is not authorized by *request*.

   :param request:  :class:`aiohttp.web.Request` object.

   :return str: authorized user ID if success

   :raise: :class:`aiohttp.web.HTTPUnauthorized` for anonymous users.

   Usage::

      async def handler(request):
          await check_authorized(request)
          # this line is never executed for anonymous users


.. coroutinefunction:: check_permission(request, permission)

   Checker that doesn't pass if user has no requested permission.

   :param request:  :class:`aiohttp.web.Request` object.

   :raise: :class:`aiohttp.web.HTTPUnauthorized` for anonymous users.

   :raise: :class:`aiohttp.web.HTTPForbidden` if user is
           authorized but has no access rights.

   Usage::

      async def handler(request):
          await check_permission(request, 'read')
          # this line is never executed if a user has no read permission


.. coroutinefunction:: authorized_userid(request)

   Retrieve :term:`userid`.

   The user should be registered by :func:`remember` before the call.

   :param request: :class:`aiohttp.web.Request` object.

   :return: :class:`str` :term:`userid` or ``None`` for session
            without signed in user.


.. coroutinefunction:: permits(request, permission, context=None)

   Check user's permission.

   Return ``True`` if user remembered in *request* has specified *permission*.

   Allowed permissions as well as *context* meaning are depends on
   :class:`AbstractAuthorizationPolicy` implementation.

   Actually it's a wrapper around
   :meth:`AbstractAuthorizationPolicy.permits` coroutine.

   The user should be registered by :func:`remember` before the call.

   :param request: :class:`aiohttp.web.Request` object.

   :param permission: Requested :term:`permission`. :class:`str` or
                      :class:`enum.Enum` object.

   :param context: additional object may be passed into
                   :meth:`AbstractAuthorizationPolicy.permission`
                   coroutine.

   :return: ``True`` if registered user has requested *permission*,
            ``False`` otherwise.


.. coroutinefunction:: is_anonymous(request)

   Checks if user is anonymous user.

   Return ``True`` if user is not remembered in request, otherwise
   returns ``False``.

   :param request: :class:`aiohttp.web.Request` object.


.. decorator:: login_required

   Decorator for handlers that checks if user is authorized.

   Raises :class:`aiohttp.web.HTTPUnauthorized` if user is not authorized.

   .. deprecated:: 0.3

      Use :func:`check_authorized` async function.


.. decorator:: has_permission(permission)

   Decorator for handlers that checks if user is authorized
   and has correct permission.

   Raises :class:`aiohttp.web.HTTPUnauthorized` if user is not
   authorized.

   Raises :class:`aiohttp.web.HTTPForbidden` if user is
   authorized but has no access rights.

   :param str permission: requested :term:`permission`.

   .. deprecated:: 0.3

      Use :func:`check_authorized` async function.


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


Authorization policy
---------------------

.. class:: AbstractAuthorizationPolicy

   .. coroutinemethod:: authorized_userid(identity)

      Retrieve authorized user id.

      Abstract method, should be overriden by descendant.

      :param identity: an :term:`identity` used for authorization.

      :return: the :term:`userid` of the user identified by the
               *identity* or ``None`` if no user exists related to the
               identity.

   .. coroutinemethod:: permits(identity, permission, context=None)

      Check user permissions.

      Abstract method, should be overriden by descendant.

      :param identity: an :term:`identity` used for authorization.

      :param permission: requested permission. The type of parameter
                         is not fixed and depends on implementation.
