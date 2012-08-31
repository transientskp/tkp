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
