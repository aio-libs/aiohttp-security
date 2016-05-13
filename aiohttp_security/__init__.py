from .abc import AbstractIdentityPolicy, AbstractAuthorizationPolicy
from .api import remember, forget, setup, authorize, permits, get_user_identity
from .cookies_identity import CookiesIdentityPolicy
from .session_identity import SessionIdentityPolicy


__version__ = '0.1.0'


__all__ = ('AbstractIdentityPolicy', 'AbstractAuthorizationPolicy',
           'CookiesIdentityPolicy', 'SessionIdentityPolicy',
           'remember', 'forget', 'authorize', 'permits',
           'get_user_identity', 'setup')
