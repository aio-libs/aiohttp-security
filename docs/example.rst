.. _aiohttp-security-example:

===============================================
How to Make a Simple Server With Authorization
===============================================


Simple example::

    import asyncio
    from aiohttp import web

    @asyncio.coroutine
    def root_handler(request):
        text = "Alive and kicking!"
        return web.Response(body=text.encode('utf-8'))

    # option 2: auth at a higher level?
    # set user_id and allowed in the wsgi handler
    @protect('view_user')
    @asyncio.coroutine
    def user_handler(request):
        name = request.match_info.get('name', "Anonymous")
        text = "Hello, " + name
        return web.Response(body=text.encode('utf-8'))


    # option 3: super low
    # wsgi doesn't do anything
    @asyncio.coroutine
    def user_update_handler(request):
        # identity, asked_permission
        user_id = yield from identity_policy.identify(request)
        identity = yield from auth_policy.authorized_user_id(user_id)
        allowed = yield from request.auth_policy.permits(
                identity, asked_permission
                )
        if not allowed:
            # how is this pluggable as well?
            # ? return NotAllowedStream()
            raise NotAllowedResponse()

        update_user()

    @asyncio.coroutine
    def init(loop):
        # set up identity and auth
        auth_policy = DictionaryAuthorizationPolicy({'me': ('view_user',),
                                                     'you': ('view_user',
                                                             'edit_user',)})
        identity_policy = CookieIdentityPolicy()
        auth = authorization_middleware(auth_policy, identity_policy)

        # wsgi app
        app = web.Application(loop=loop, middlewares=*auth)

        # add the routes
        app.router.add_route('GET', '/', root_handler)
        app.router.add_route('GET', '/{user}', user_handler)
        app.router.add_route('GET', '/{user}/edit', user_update_handler)

        # get it started
        srv = yield from loop.create_server(app.make_handler(),
                                            '127.0.0.1', 8080)
        print("Server started at http://127.0.0.1:8080")
        return srv


    loop = asyncio.get_event_loop()
    loop.run_until_complete(init(loop))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass  # TODO put handler cleanup here
