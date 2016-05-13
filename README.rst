aiohttp_security
================

The library provides identity and autorization for `aiohttp.web`__.

.. _aiohttp_web: http://aiohttp.readthedocs.org/en/latest/web.html

__ aiohttp_web_

Usage
-----

.. code-block:: python

  from aiohttp_security import authorize
  
  @authorize(required=True, redirect_url='/login', permission='admin')
  async def index(request, identity=None):
      return web.Response(body=b'OK')

License
-------

``aiohttp_security`` is offered under the Apache 2 license.
