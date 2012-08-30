from distutils.core import setup

setup(
    name="TKP recipes",
    version="0.1.dev",
    packages=[
        'trap.recipes',
        'trap.recipes.master',
        'trap.recipes.nodes',
    ],
    description="LOFAR Transients Key Project pipeline recipes",
    author="TKP Discovery WG",
    author_email="discovery@transientskp.org",
    url="http://www.transientskp.org/",
)
