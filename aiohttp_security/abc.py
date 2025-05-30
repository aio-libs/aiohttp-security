import abc
from enum import Enum
from typing import Any, Optional, Union

from aiohttp import web

# see http://plope.com/pyramid_auth_design_api_postmortem


class AbstractIdentityPolicy(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    async def identify(self, request: web.Request) -> Optional[str]:
        """Return the claimed identity of the user associated request or
        ``None`` if no identity can be found associated with the request."""
        pass

    @abc.abstractmethod
    async def remember(self, request: web.Request,
                       response: web.StreamResponse, identity: str, **kwargs: Any) -> None:
        """Remember identity.

        Modify response object by filling it's headers with remembered user.

        An individual identity policy and its consumers can decide on
        the composition and meaning of **kwargs.
        """
        pass

    @abc.abstractmethod
    async def forget(self, request: web.Request, response: web.StreamResponse) -> None:
        """ Modify response which can be used to 'forget' the
        current identity on subsequent requests."""
        pass


class AbstractAuthorizationPolicy(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    async def permits(self, identity: Optional[str],
                      permission: Union[str, Enum], context: Any = None) -> bool:
        """Check user permissions.

        Return True if the identity is allowed the permission in the
        current context, else return False.
        """
        pass

    @abc.abstractmethod
    async def authorized_userid(self, identity: str) -> Optional[str]:
        """Retrieve authorized user id.

        Return the user_id of the user identified by the identity
        or 'None' if no user exists related to the identity.
        """
        pass
