import asyncio
from aiohttp import web
from aiohttp_security.abc import (AbstractIdentityPolicy,
                                  AbstractAuthorizationPolicy)

IDENTITY_KEY = 'aiohttp_security_identity_policy'
AUTZ_KEY = 'aiohttp_security_autz_policy'


@asyncio.coroutine
def remember(request, response, identity, **kwargs):
    """Remember identity into response.

    The action is performed by indentity_policy.remember()
    Usually the idenity is stored in user cookies homehow.
    """
    assert isinstance(identity, str), identity
    identity_policy = request.app.get(IDENTITY_KEY)
    if identity_policy is None:
        text = ("Security subsystem is not initialized, "
                "call aiohttp_security.setup(...) first")
        # in order to see meaningful exception message both: on console
        # output and rendered page we add same message to *reason* and
        # *text* arguments.
        raise web.HTTPInternalServerError(reason=text, text=text)
    yield from identity_policy.remember(request, response, identity, **kwargs)


@asyncio.coroutine
def forget(request, response):
    identity_policy = request.app.get(IDENTITY_KEY)
    if identity_policy is None:
        text = ("Security subsystem is not initialized, "
                "call aiohttp_security.setup(...) first")
        # in order to see meaningful exception message both: on console
        # output and rendered page we add same message to *reason* and
        # *text* arguments.
        raise web.HTTPInternalServerError(reason=text, text=text)
    yield from identity_policy.forget(request, response)


@asyncio.coroutine
def authorized_userid(request):
    identity_policy = request.app.get(IDENTITY_KEY)
    autz_policy = request.app.get(AUTZ_KEY)
    if identity_policy is None or autz_policy is None:
        return None
    identity = yield from identity_policy.identify(request)
    user_id = yield from autz_policy.authorized_userid(identity)
    return user_id


@asyncio.coroutine
def permits(request, permission, context=None):
    identity_policy = request.app.get(IDENTITY_KEY)
    autz_policy = request.app.get(AUTZ_KEY)
    if identity_policy is None or autz_policy is None:
        return True
    identity = yield from identity_policy.identify(request)
    access = yield from autz_policy.permits(identity, permission, context)
    return access


def setup(app, identity_policy, autz_policy):
    assert isinstance(identity_policy, AbstractIdentityPolicy), identity_policy
    assert isinstance(autz_policy, AbstractAuthorizationPolicy), autz_policy

    app[IDENTITY_KEY] = identity_policy
    app[AUTZ_KEY] = autz_policy
