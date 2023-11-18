from .abc import AbstractAuthorizationPolicy, AbstractIdentityPolicy
from .api import (authorized_userid, check_authorized, check_permission, forget,
                  is_anonymous, permits, remember, setup)
from .cookies_identity import CookiesIdentityPolicy
from .jwt_identity import JWTIdentityPolicy
from .session_identity import SessionIdentityPolicy

__version__ = '0.5.0'


__all__ = ('AbstractIdentityPolicy', 'AbstractAuthorizationPolicy',
           'CookiesIdentityPolicy', 'SessionIdentityPolicy',
           'JWTIdentityPolicy',
           'remember', 'forget', 'authorized_userid',
           'permits', 'setup', 'is_anonymous',
           'check_authorized', 'check_permission')
