from distutils.core import setup

setup(
    name="TKP recipes",
    version="0.1.dev",
    packages=[
        'recipes',
        'recipes.master',
        'recipes.nodes',
    ],
    description="LOFAR Transients Key Project pipeline recipes",
    author="TKP Software WG",
    author_email="software@transientskp.org",
    url="http://www.transientskp.org/",
)
