#!/usr/bin/env python
from setuptools import setup, find_packages

install_requires = """
    astropy
    colorlog
    Jinja2
    numpy
    psycopg2
    python-casacore
    python-dateutil
    pytz
    scipy
    sqlalchemy<2
    alembic
    monotonic
    psutil
    pytest
    dask
    dask[array]
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
