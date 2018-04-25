from aiohttp import web
from aiohttp_session import SimpleCookieStorage, session_middleware
from aiohttp_security import has_permission, \
    is_anonymous, remember, forget, \
    setup as setup_security, SessionIdentityPolicy
from aiohttp_security.abc import AbstractAuthorizationPolicy


# Demo authorization policy for only one user.
# User 'jack' has only 'listen' permission.
# For more complicated authorization policies see examples
# in the 'demo' directory.
class SimpleJack_AuthorizationPolicy(AbstractAuthorizationPolicy):
    async def authorized_userid(self, identity):
        """Retrieve authorized user id.
        Return the user_id of the user identified by the identity
        or 'None' if no user exists related to the identity.
        """
        if identity == 'jack':
            return identity

    async def permits(self, identity, permission, context=None):
        """Check user permissions.
        Return True if the identity is allowed the permission
        in the current context, else return False.
        """
        return identity == 'jack' and permission in ('listen',)


async def handler_root(request):
    is_logged = not await is_anonymous(request)
    return web.Response(text='''<html><head></head><body>
            Hello, I'm Jack, I'm {logged} logged in.<br /><br />
            <a href="/login">Log me in</a><br />
            <a href="/logout">Log me out</a><br /><br />
            Check my permissions,
            when i'm logged in and logged out.<br />
            <a href="/listen">Can I listen?</a><br />
            <a href="/speak">Can I speak?</a><br />
        </body></html>'''.format(
            logged='' if is_logged else 'NOT',
        ), content_type='text/html')


async def handler_login_jack(request):
    redirect_response = web.HTTPFound('/')
    await remember(request, redirect_response, 'jack')
    raise redirect_response


async def handler_logout(request):
    redirect_response = web.HTTPFound('/')
    await forget(request, redirect_response)
    raise redirect_response


@has_permission('listen')
async def handler_listen(request):
    return web.Response(body="I can listen!")


@has_permission('speak')
async def handler_speak(request):
    return web.Response(body="I can speak!")


async def make_app():
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
