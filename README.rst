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

The library provides identity and autorization for `aiohttp.web`__.

.. _aiohttp_web: http://aiohttp.readthedocs.org/en/latest/web.html

__ aiohttp_web_

Usage
-----
To install type ``pip install aiohttp_security``.
Launch ``make doc`` and see examples or look under **demo** directory for a
sample project.

Documentation
-------------

https://aiohttp-security.readthedocs.io/

Develop
-------

``pip install -r requirements-dev``

.. code-block:: python

  from aiohttp_security import authorize
  
  @authorize(required=True, redirect_url='/login', permission='admin')
  async def index(request, identity=None):
      return web.Response(body=b'OK')

License
-------

``aiohttp_security`` is offered under the Apache 2 license.
