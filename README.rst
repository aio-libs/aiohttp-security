aiohttp_security
================
.. image:: https://travis-ci.org/aio-libs/aiohttp-security.svg?branch=master
    :target: https://travis-ci.org/aio-libs/aiohttp-security
.. image:: https://codecov.io/github/aio-libs/aiohttp-security/coverage.svg?branch=master
    :target: https://codecov.io/github/aio-libs/aiohttp-security
.. image:: https://readthedocs.org/projects/aiohttp-security/badge/?version=latest
    :target: https://aiohttp-security.readthedocs.io/
.. image:: https://img.shields.io/pypi/v/aiohttp-security.svg
    :target: https://pypi.python.org/pypi/aiohttp-security

The library provides identity and authorization for `aiohttp.web`__.

.. _aiohttp_web: http://aiohttp.readthedocs.org/en/latest/web.html

__ aiohttp_web_

Installation
------------
Simplest case (authorization via cookies) ::

    $ pip install aiohttp_security

With `aiohttp-session` support ::

    $ pip install aiohttp_security[session]

Examples
--------
Take a look at examples:

`Basic example`_

`Example with DB auth`_

.. _`Basic example`: docs/example.rst
.. _`Example with db auth`: docs/example_db_auth.rst

and demos at **demo** directory.

Documentation
-------------

https://aiohttp-security.readthedocs.io/

Develop
-------

``pip install -r requirements-dev.txt``


License
-------

``aiohttp_security`` is offered under the Apache 2 license.
