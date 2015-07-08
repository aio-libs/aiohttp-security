import asyncio
from aiohttp_security.abc import (AbstractIdentityPolicy,
                                  AbstractAuthorizationPolicy)

IDENTITY_KEY = 'aiohttp_security_identity_policy'
AUTZ_KEY = 'aiohttp_security_autz_policy'


@asyncio.coroutine
def remember(request, identity, **kwargs):
    identity_policy = request.app[IDENTITY_KEY]
    headers = yield from identity_policy.remember(request, identity, **kwargs)
    return headers


@asyncio.coroutine
def forget(request):
    identity_policy = request.app[IDENTITY_KEY]
    headers = yield from identity_policy.forget(request)
    return headers


@asyncio.coroutine
def authorized_userid(request):
    identity_policy = request.app[IDENTITY_KEY]
    autz_policy = request.app[AUTZ_KEY]
    identity = yield from identity_policy.identify(request)
    user_id = yield from autz_policy.authorized_userid(identity)
    return user_id


@asyncio.coroutine
def permits(request, permission, context=None):
    identity_policy = request.app[IDENTITY_KEY]
    autz_policy = request.app[AUTZ_KEY]
    identity = yield from identity_policy.identify(request)
    access = yield from autz_policy.permits(identity, permission, context)
    return access


def setup(app, identity_policy, auth_policy):
    assert isinstance(identity_policy, AbstractIdentityPolicy), identity_policy
    assert isinstance(auth_policy, AbstractAuthorizationPolicy), auth_policy

    app[IDENTITY_KEY] = identity_policy
    app[AUTZ_KEY] = auth_policy
