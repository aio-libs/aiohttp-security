from .abc import AbstractIdentityPolicy, AbstractAuthorizationPolicy
from .api import (
    authorized_userid,
    forget,
    login_required,
    permits,
    remember,
    setup,
)
from .cookies_identity import CookiesIdentityPolicy
from .session_identity import SessionIdentityPolicy


__version__ = '0.1.1'


__all__ = ('AbstractIdentityPolicy', 'AbstractAuthorizationPolicy',
           'CookiesIdentityPolicy', 'SessionIdentityPolicy',
           'remember', 'forget', 'authorized_userid',
           'permits', 'setup', 'login_required')
