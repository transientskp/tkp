#!/usr/bin/env python

import os
from setuptools import setup

install_requires = """
    numpy>=1.3.0
    scipy>=0.7.0
    pyfits>=2.3.1
    python-dateutil>=1.4.1
    pytz
    pywcs>=1.12
    python-casacore
    psycopg2
    """.split()

extras_require = {
    'pixelstore': ['pymongo'],
    'monetdb' : ['python-monetdb>=11.11.11'],
    'distribute' : [ 'celery>=3.1.11']
}

tkp_scripts = [
    "tkp/bin/pyse.py",
    "tkp/bin/trap-manage.py",
    "tkp/bin/tkp-inject.py",
    ]

def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)


tkp_packages = []
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)

for dirpath, dirnames, filenames in os.walk('tkp'):
    # Ignore dirnames that start with '.'
    dirnames[:] = [d for d in dirnames if not d.startswith('.') and d != '__pycache__']
    if '__init__.py' in filenames:
        tkp_packages.append('.'.join(fullsplit(dirpath)))


package_data = {'tkp': [
    'config/*/*',
    'db/sql/statements/batch',
    'db/sql/statements/*/*.sql'
]}


from tkp import __version__ as tkp_version

setup(
    name = "tkp",
    version = tkp_version,
    packages = tkp_packages,
    scripts = tkp_scripts,
    package_data=package_data,
    description = "LOFAR Transients Key Project (TKP)",
    author = "TKP Discovery WG",
    author_email = "discovery@transientskp.org",
    url = "http://docs.transientskp.org/",
    install_requires=install_requires,
    extras_require=extras_require
)
