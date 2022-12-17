from enum import Enum
from typing import NoReturn, Optional, Union

from aiohttp import web
from aiohttp_session import SimpleCookieStorage, session_middleware

from aiohttp_security import (SessionIdentityPolicy, check_permission, forget,
                              is_anonymous, remember, setup as setup_security)
from aiohttp_security.abc import AbstractAuthorizationPolicy


# Demo authorization policy for only one user.
# User 'jack' has only 'listen' permission.
# For more complicated authorization policies see examples
# in the 'demo' directory.
class SimpleJack_AuthorizationPolicy(AbstractAuthorizationPolicy):
    async def authorized_userid(self, identity: str) -> Optional[str]:
        """Retrieve authorized user id.
        Return the user_id of the user identified by the identity
        or 'None' if no user exists related to the identity.
        """
        return identity if identity == "jack" else None

    async def permits(self, identity: Optional[str], permission: Union[str, Enum],
                      context: None = None) -> bool:
        """Check user permissions.
        Return True if the identity is allowed the permission
        in the current context, else return False.
        """
        return identity == 'jack' and permission in ('listen',)


async def handler_root(request: web.Request) -> web.Response:
    tmpl = """<html><head></head><body>
        Hello, I'm Jack, I'm {} logged in.<br /><br />
        <a href="/login">Log me in</a><br />
        <a href="/logout">Log me out</a><br /><br />
        Check my permissions, when I'm logged in and logged out.<br />
        <a href="/listen">Can I listen?</a><br />
        <a href="/speak">Can I speak?</a><br />
    </body></html>"""
    is_logged = not await is_anonymous(request)
    return web.Response(text=tmpl.format("" if is_logged else "NOT"), content_type="text/html")


async def handler_login_jack(request: web.Request) -> NoReturn:
    redirect_response = web.HTTPFound('/')
    await remember(request, redirect_response, 'jack')
    raise redirect_response


async def handler_logout(request: web.Request) -> NoReturn:
    redirect_response = web.HTTPFound('/')
    await forget(request, redirect_response)
    raise redirect_response


async def handler_listen(request: web.Request) -> web.Response:
    await check_permission(request, 'listen')
    return web.Response(body="I can listen!")


async def handler_speak(request: web.Request) -> web.Response:
    await check_permission(request, 'speak')
    return web.Response(body="I can speak!")


async def make_app() -> web.Application:
    #
    # WARNING!!!
    # Never use SimpleCookieStorage on production!!!
    # It’s highly insecure!!!
    #

    # make app
    middleware = session_middleware(SimpleCookieStorage())
    app = web.Application(middlewares=[middleware])

    # add the routes
    app.router.add_route('GET', '/', handler_root)
    app.router.add_route('GET', '/login', handler_login_jack)
    app.router.add_route('GET', '/logout', handler_logout)
    app.router.add_route('GET', '/listen', handler_listen)
    app.router.add_route('GET', '/speak', handler_speak)

    # set up policies
    policy = SessionIdentityPolicy()
    setup_security(app, policy, SimpleJack_AuthorizationPolicy())

    return app


if __name__ == '__main__':
    web.run_app(make_app(), port=9000)
