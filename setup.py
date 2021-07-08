#!/usr/bin/env python
from setuptools import setup, find_packages

install_requires = """
    astropy<3.0.0
    colorlog
    numpy>=1.3.0,<1.17.0
    psycopg2
    python-casacore
    python-dateutil>=1.4.1
    pytz
    scipy>=0.7.0,<1.3.0
    sqlalchemy>=1.0.0
    alembic
    monotonic
    """.split()

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
    name="tkp",
    version="4.0",
    packages=package_list,
    scripts=tkp_scripts,
    package_data=package_data,
    description="LOFAR Transients Key Project (TKP)",
    author="TKP Discovery WG",
    author_email="discovery@transientskp.org",
    url="http://docs.transientskp.org/",
    install_requires=install_requires
)
