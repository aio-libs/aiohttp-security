from enum import Enum
from typing import Dict, Optional, Union

from aiohttp_security.abc import AbstractAuthorizationPolicy

from .users import User


class DictionaryAuthorizationPolicy(AbstractAuthorizationPolicy):
    def __init__(self, user_map: Dict[str, User]):
        super().__init__()
        self.user_map = user_map

    async def authorized_userid(self, identity: str) -> Optional[str]:
        """Retrieve authorized user id.
        Return the user_id of the user identified by the identity
        or 'None' if no user exists related to the identity.
        """
        return identity if identity in self.user_map else None

    async def permits(self, identity: str, permission: Union[str, Enum],
                      context: None = None) -> bool:
        """Check user permissions.
        Return True if the identity is allowed the permission in the
        current context, else return False.
        """
        # pylint: disable=unused-argument
        user = self.user_map.get(identity)
        if not user:
            return False
        return permission in user.permissions


async def check_credentials(user_map: Dict[str, User], username: str, password: str) -> bool:
    user = user_map.get(username)
    if not user:
        return False

    return user.password == password
