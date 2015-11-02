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

   identity

      Session-wide :class:`str` for identifying user.

      Stored in local storage (client-side cookie or server-side storage).

      Use :coroutine:`~aiohttp_session.remember` for saving *identity* (login)
      and :coroutine:`~aiohttp_session.forget` for dropping it (logout).

      *identity* is used for getting :term:`userid` and :term:`permissions`.

   userid

       User's ID, most likely his *login* or *email*
