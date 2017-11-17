from .abc import AbstractAuthorizationPolicy, AbstractIdentityPolicy
from .api import (authorized_userid, forget, has_permission, is_anonymous,
                  login_required, permits, remember, setup)
from .cookies_identity import CookiesIdentityPolicy
from .session_identity import SessionIdentityPolicy

__version__ = '0.2.0'


__all__ = ('AbstractIdentityPolicy', 'AbstractAuthorizationPolicy',
           'CookiesIdentityPolicy', 'SessionIdentityPolicy',
           'remember', 'forget', 'authorized_userid',
           'permits', 'setup', 'is_anonymous',
           'login_required', 'has_permission')
