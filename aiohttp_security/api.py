import enum
import warnings
from functools import wraps
from typing import Any, Callable, Optional, TypeVar, Union

from aiohttp import web
from aiohttp_security.abc import AbstractAuthorizationPolicy, AbstractIdentityPolicy

IDENTITY_KEY = 'aiohttp_security_identity_policy'
AUTZ_KEY = 'aiohttp_security_autz_policy'

# _AIP/_AAP are shorthand for Optional[policy] when we retrieve from request.
_AAP = Optional[AbstractAuthorizationPolicy]
_AIP = Optional[AbstractIdentityPolicy]


async def remember(request: web.Request, response: web.StreamResponse,
                   identity: str, **kwargs: Any) -> None:
    """Remember identity into response.

    The action is performed by identity_policy.remember()

    Usually the identity is stored in user cookies somehow but may be
    pushed into custom header also.
    """
    if not identity or not isinstance(identity, str):
        raise ValueError("Identity should be a str value.")
    identity_policy = request.config_dict.get(IDENTITY_KEY)
    if identity_policy is None:
        text = ("Security subsystem is not initialized, "
                "call aiohttp_security.setup(...) first")
        # in order to see meaningful exception message both: on console
        # output and rendered page we add same message to *reason* and
        # *text* arguments.
        raise web.HTTPInternalServerError(reason=text, text=text)
    await identity_policy.remember(request, response, identity, **kwargs)


async def forget(request: web.Request, response: web.StreamResponse) -> None:
    """Forget previously remembered identity.

    Usually it clears cookie or server-side storage to forget user
    session.
    """
    identity_policy = request.config_dict.get(IDENTITY_KEY)
    if identity_policy is None:
        text = ("Security subsystem is not initialized, "
                "call aiohttp_security.setup(...) first")
        # in order to see meaningful exception message both: on console
        # output and rendered page we add same message to *reason* and
        # *text* arguments.
        raise web.HTTPInternalServerError(reason=text, text=text)
    await identity_policy.forget(request, response)


async def authorized_userid(request: web.Request) -> Optional[str]:
    identity_policy: _AIP = request.config_dict.get(IDENTITY_KEY)
    autz_policy: _AAP = request.config_dict.get(AUTZ_KEY)
    if identity_policy is None or autz_policy is None:
        return None
    identity = await identity_policy.identify(request)
    if identity is None:
        return None  # non-registered user has None user_id
    user_id = await autz_policy.authorized_userid(identity)
    return user_id


async def permits(request: web.Request, permission: Union[str, enum.Enum],
                  context: Any = None) -> bool:
    if not permission or not isinstance(permission, (str, enum.Enum)):
        raise ValueError("Permission should be a str or enum value.")
    identity_policy: _AIP = request.config_dict.get(IDENTITY_KEY)
    autz_policy: _AAP = request.config_dict.get(AUTZ_KEY)
    if identity_policy is None or autz_policy is None:
        return True
    identity = await identity_policy.identify(request)
    # non-registered user still may have some permissions
    access = await autz_policy.permits(identity, permission, context)
    return access


async def is_anonymous(request: web.Request) -> bool:
    """Check if user is anonymous.

    User is considered anonymous if there is not identity
    in request.
    """
    identity_policy = request.config_dict.get(IDENTITY_KEY)
    if identity_policy is None:
        return True
    identity = await identity_policy.identify(request)
    if identity is None:
        return True
    return False


async def check_authorized(request: web.Request) -> str:
    """Checker that raises HTTPUnauthorized for anonymous users.
    """
    userid = await authorized_userid(request)
    if userid is None:
        raise web.HTTPUnauthorized()
    return userid


async def check_permission(request: web.Request, permission: Union[str, enum.Enum],
                           context: Any = None) -> None:
    """Checker that passes only to authoraised users with given permission.

    If user is not authorized - raises HTTPUnauthorized,
    if user is authorized and does not have permission -
    raises HTTPForbidden.
    """

    await check_authorized(request)
    allowed = await permits(request, permission, context)
    if not allowed:
        raise web.HTTPForbidden()


def setup(app: web.Application, identity_policy: AbstractIdentityPolicy,
          autz_policy: AbstractAuthorizationPolicy) -> None:
    if not isinstance(identity_policy, AbstractIdentityPolicy):
        raise ValueError("Identity policy is not subclass of AbstractIdentityPolicy")
    if not isinstance(autz_policy, AbstractAuthorizationPolicy):
        raise ValueError("Authentication policy is not subclass of AbstractAuthorizationPolicy")

    app[IDENTITY_KEY] = identity_policy
    app[AUTZ_KEY] = autz_policy
