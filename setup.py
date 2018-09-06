from setuptools import setup, find_packages
import os
import re
import subprocess
import sys

from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    user_options = []

    def run(self):
        errno = subprocess.call([sys.executable, '-m', 'pytest', 'tests'])
        raise SystemExit(errno)


with open(os.path.join(os.path.abspath(os.path.dirname(
        __file__)), 'aiohttp_security', '__init__.py'), 'r', encoding='latin1') as fp:
    try:
        version = re.findall(r"^__version__ = '([^']+)'$", fp.read(), re.M)[0]
    except IndexError:
        raise RuntimeError('Unable to determine version.')


def read(f):
    return open(os.path.join(os.path.dirname(__file__), f)).read().strip()


install_requires = ['aiohttp>=3.0.0']
tests_require = install_requires + ['pytest']
extras_require = {'session': 'aiohttp-session'}


setup(name='aiohttp-security',
      version=version,
      description=("security for aiohttp.web"),
      long_description='\n\n'.join((read('README.rst'), read('CHANGES.txt'))),
      classifiers=[
          'License :: OSI Approved :: Apache Software License',
          'Intended Audience :: Developers',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Topic :: Internet :: WWW/HTTP',
          'Framework :: AsyncIO',
      ],
      author='Andrew Svetlov',
      author_email='andrew.svetlov@gmail.com',
      url='https://github.com/aio-libs/aiohttp_security/',
      license='Apache 2',
      packages=find_packages(),
      install_requires=install_requires,
      tests_require=tests_require,
      cmdclass={'test': PyTest},
      include_package_data=True,
      extras_require=extras_require)
