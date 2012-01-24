from distutils.core import setup

setup(
    name="TKP Libraries",
    version="0.1.dev",
    packages=[
        'tkp',
        'tkp.database',
        'tkp.sourcefinder',
        'tkp.classification',
        'tkp.classification.features',
        'tkp.classification.transient',
        'tkp.classification.manual',
        'tkp.tests',
        'tkp.tests.utility',
        'tkp.utility'
    ],
    description="LOFAR Transients Key Project Python libraries",
    author="TKP Discovery WG",
    author_email="discovery@transientskp.org",
    url="http://www.transientskp.org/",
)
