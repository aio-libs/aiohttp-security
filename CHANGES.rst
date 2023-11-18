=======
CHANGES
=======

.. towncrier release notes start

0.5.0 (2023-11-18)
==================

- Added type annotations.
- Added a reason message when permission is rejected.
- Switched to ``aiohttp.web.AppKey``.
- Reverted change in ``JWTIdentityPolicy`` so identity returns ``str``.

0.4.0 (2018-09-27)
==================

- Bump minimal supported ``aiohttp`` version to 3.2.
- Use ``request.config_dict`` for accessing ``jinja2`` environment. It
  allows to reuse jinja rendering engine from parent application.

0.3.0 (2018-09-06)
==================

- Deprecate ``login_required`` and ``has_permission`` decorators.
  Use ``check_authorized`` and ``check_permission`` helper functions instead.
- Bump supported ``aiohttp`` version to 3.0+.
- Enable strong warnings mode for test suite, clean-up all deprecation warnings.
- Polish documentation

0.2.0 (2017-11-17)
==================

- Add ``is_anonymous``, ``login_required``, ``has_permission`` helpers. (#114)

0.1.2 (2017-10-17)
==================

- Make aiohttp-session optional dependency. (#107)
