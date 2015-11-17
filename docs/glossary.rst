.. _aiohttp-security-glossary:

==========
 Glossary
==========

.. if you add new entries, keep the alphabetical sorting!

.. glossary::


   aiohttp

      :term:`asyncio` based library for making web servers.


   asyncio

      The library for writing single-threaded concurrent code using
      coroutines, multiplexing I/O access over sockets and other
      resources, running network clients and servers, and other
      related primitives.

      Reference implementation of :pep:`3156`

      https://pypi.python.org/pypi/asyncio/

   authentication

      Actions related to retrieving, storing and removing user's
      :term:`identity`.

      Authenticated user has no access rights, the system even has no
      knowledge is there the user still registered in DB.

      If :class:`~aiohttp.web.Request` has an :term:`identity` it
      means the user has some ID that should be checked by
      :term:`authorization` policy.

   authorization

      Checking actual permissions for identified user along with
      getting :term:`userid`.

   identity

      Session-wide :class:`str` for identifying user.

      Stored in local storage (client-side cookie or server-side storage).

      Use :meth:`~aiohttp_session.remember` for saving *identity* (sign in)
      and :meth:`~aiohttp_session.forget` for dropping it (sign out).

      *identity* is used for getting :term:`userid` and :term:`permission`.

   permission

      Permission required for access to resource.

      Permissions are just strings, and they have no required
      composition: you can name permissions whatever you like.

   userid

       User's ID, most likely his *login* or *email*
