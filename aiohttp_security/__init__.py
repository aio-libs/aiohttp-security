from .abc import AbstractAuthorizationPolicy, AbstractIdentityPolicy
from .api import (authorized_userid, check_authorized, check_permission, forget, has_permission,
                  is_anonymous, login_required, permits, remember, setup)
from .cookies_identity import CookiesIdentityPolicy
from .jwt_identity import JWTIdentityPolicy
from .session_identity import SessionIdentityPolicy

__version__ = '0.4.0'


__all__ = ('AbstractIdentityPolicy', 'AbstractAuthorizationPolicy',
           'CookiesIdentityPolicy', 'SessionIdentityPolicy',
           'JWTIdentityPolicy',
           'remember', 'forget', 'authorized_userid',
           'permits', 'setup', 'is_anonymous',
           'login_required', 'has_permission',
           'check_authorized', 'check_permission')
