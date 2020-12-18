import base64
from cryptography import fernet
from aiohttp import web
from aiohttp_session import setup as setup_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from aiohttp_security import setup as setup_security
from aiohttp_security import SessionIdentityPolicy

from demo.dictionary_auth.authz import DictionaryAuthorizationPolicy
from demo.dictionary_auth.handlers import configure_handlers
from demo.dictionary_auth.users import user_map


def make_app() -> web.Application:
    app = web.Application()
    app['user_map'] = user_map
    configure_handlers(app)

    # secret_key must be 32 url-safe base64-encoded bytes
    fernet_key = fernet.Fernet.generate_key()
    secret_key = base64.urlsafe_b64decode(fernet_key)

    storage = EncryptedCookieStorage(secret_key, cookie_name='API_SESSION')
    setup_session(app, storage)

    policy = SessionIdentityPolicy()
    setup_security(app, policy, DictionaryAuthorizationPolicy(user_map))

    return app


if __name__ == '__main__':
    web.run_app(make_app(), port=9000)
