"""Identity policy for storing info directly into HTTP cookie.

Use mostly for demonstration purposes, SessionIdentityPolicy is much
more handy.

"""

from aiohttp import web
from typing import Any, NewType, Optional, Union, cast

from .abc import AbstractIdentityPolicy

_Sentinel = NewType('_Sentinel', object)
sentinel = _Sentinel(object())


class CookiesIdentityPolicy(AbstractIdentityPolicy):

    def __init__(self) -> None:
        self._cookie_name = 'AIOHTTP_SECURITY'
        self._max_age = 30 * 24 * 3600

    async def identify(self, request: web.Request) -> Optional[str]:
        return request.cookies.get(self._cookie_name)

    async def remember(self, request: web.Request, response: web.StreamResponse,
                       identity: str, max_age: Union[_Sentinel, Optional[int]] = sentinel,
                       **kwargs: Any) -> None:
        if max_age is sentinel:
            max_age = self._max_age
        max_age = cast(Optional[int], max_age)
        response.set_cookie(self._cookie_name, identity,
                            max_age=max_age, **kwargs)

    async def forget(self, request: web.Request, response: web.StreamResponse) -> None:
        response.del_cookie(self._cookie_name)
