#!/usr/bin/env python

from distutils.core import setup

setup(
    name="tkp",
    version="0.1",
    packages=[
        'tkp',
        'tkp.database',
        'tkp.database.utils',
        'tkp.sourcefinder',
        'tkp.classification',
        'tkp.classification.features',
        'tkp.classification.transient',
        'tkp.classification.manual',
        'tkp.utility',
        'tkp.utility.accessors'
    ],
    description="LOFAR Transients Key Project (TKP)",
    author="TKP Discovery WG",
    author_email="discovery@transientskp.org",
    url="http://www.transientskp.org/",
)

# use numpy to compile fortran stuff into python module
from numpy.distutils.core import setup, Extension
setup(
  name="deconv",
  version="1.0",
  ext_modules = [Extension( 'deconv', ['external/deconv/deconv.f'] )],
)
