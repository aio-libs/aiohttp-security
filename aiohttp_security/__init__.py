from .abc import AbstractAuthorizationPolicy, AbstractIdentityPolicy
from .api import (authorized_userid, forget, has_permission,
                  is_anonymous, login_required, permits, remember,
                  setup, check_authorized, check_permission)
from .cookies_identity import CookiesIdentityPolicy
from .session_identity import SessionIdentityPolicy
from .jwt_identity import JWTIdentityPolicy

__version__ = '0.4.0'


__all__ = ('AbstractIdentityPolicy', 'AbstractAuthorizationPolicy',
           'CookiesIdentityPolicy', 'SessionIdentityPolicy',
           'JWTIdentityPolicy',
           'remember', 'forget', 'authorized_userid',
           'permits', 'setup', 'is_anonymous',
           'login_required', 'has_permission',
           'check_authorized', 'check_permission')
