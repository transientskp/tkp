#!/usr/bin/env python
from setuptools import setup, find_packages
from tkp import __version__ as tkp_version

install_requires = """
    numpy>=1.3.0
    scipy>=0.7.0
    astropy
    python-dateutil>=1.4.1
    pytz
    pywcs>=1.12
    python-casacore
    psycopg2
    sqlalchemy>=1.0.0
    """.split()

extras_require = {
    'pixelstore': ['pymongo'],
    'monetdb': ['python-monetdb>=11.11.11', 'sqlalchemy_monetdb>=0.9.1'],
    'distribute' : [ 'celery>=3.1.11']
}

tkp_scripts = [
    "tkp/bin/pyse.py",
    "tkp/bin/trap-manage.py",
    "tkp/bin/tkp-inject.py",
    ]

package_data = {'tkp': [
    'config/*/*',
    'db/sql/statements/batch',
    'db/sql/statements/*/*.sql'
]}

package_list = find_packages(where='.', exclude=['tests'])

setup(
    name = "tkp",
    version = tkp_version,
    packages = package_list,
    scripts = tkp_scripts,
    package_data=package_data,
    description = "LOFAR Transients Key Project (TKP)",
    author = "TKP Discovery WG",
    author_email = "discovery@transientskp.org",
    url = "http://docs.transientskp.org/",
    install_requires=install_requires,
    extras_require=extras_require
)
