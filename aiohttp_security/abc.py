import abc
import asyncio

# see http://plope.com/pyramid_auth_design_api_postmortem


class AbstractIdentityPolicy(metaclass=abc.ABCMeta):

    @asyncio.coroutine
    @abc.abstractmethod
    def identify(self, request):
        """Return the claimed identity of the user associated request or
        ``None`` if no identity can be found associated with the request."""
        pass

    @asyncio.coroutine
    @abc.abstractmethod
    def remember(self, request, response, identity, **kwargs):
        """Remember identity.

        Modify response object by filling it's headers with remembered user.

        An individual identity policy and its consumers can decide on
        the composition and meaning of **kwargs.
        """
        pass

    @asyncio.coroutine
    @abc.abstractmethod
    def forget(self, request, response):
        """ Modify response which can be used to 'forget' the
        current identity on subsequent requests."""
        pass


class AbstractAuthorizationPolicy(metaclass=abc.ABCMeta):

    @asyncio.coroutine
    @abc.abstractmethod
    def permits(self, identity, permission, context=None):
        """Check user permissions.

        Return True if the identity is allowed the permission in the
        current context, else return False.
        """
        pass

    @asyncio.coroutine
    @abc.abstractmethod
    def authorized_userid(self, identity):
        """Retrieve authorized user id.

        Return the user_id of the user identified by the identity
        or 'None' if no user exists related to the identity.
        """
        pass
