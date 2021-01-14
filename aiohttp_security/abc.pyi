import abc
import enum
from typing import Any, Optional, Union

import aiohttp.web

Context = object
OptionalContext = Optional[Context]
Permission = Union[str, enum.Enum]
UserId = str
Identity = str

class AbstractIdentityPolicy(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    async def identify(self, request: aiohttp.web.Request) -> Optional[Identity]: ...
    @abc.abstractmethod
    async def remember(self, request: aiohttp.web.Request, response: aiohttp.web.StreamResponse, identity: Identity, **kwargs: Any) -> None: ...
    @abc.abstractmethod
    async def forget(self, request: aiohttp.web.Request, response: aiohttp.web.StreamResponse) -> None: ...

class AbstractAuthorizationPolicy(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    async def permits(self, identity: Identity, permission: Permission, context: OptionalContext = ...) -> bool: ...
    @abc.abstractmethod
    async def authorized_userid(self, identity: Identity) -> Optional[UserId]: ...
