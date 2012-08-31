#!/usr/bin/env python

from distutils.core import setup

setup(
    name="trap",
    version="0.1-dev",
    packages=['trap',
              'trap.conf',
              'trap.recipes',
              'trap.recipes.nodes',
              'trap.recipes.master',
              'trap.bin',
              'trap.management'
    ],
    description="LOFAR Transients pipeline (TRAP)",
    author="TKP Discovery WG",
    author_email="discovery@transientskp.org",
    url="http://www.transientskp.org/",
)
