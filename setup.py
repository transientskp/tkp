from distutils.core import setup

setup(
    name="TKP Libraries",
    version="0.1.dev",
    packages=[
        'tkp',
        'tkp.database',
        'tkp.sourcefinder',
        'tkp.classification',
        'tkp.classification.manual',
        'tkp.classification.manual.etree',
        'tkp.classification.features',
        'tkp.classification.database',
        'tkp.tests',
        'tkp.utility'
    ],
    description="LOFAR Transients Key Project Python libraries",
    author="TKP Software WG",
    author_email="software@transientskp.org",
    url="http://www.transientskp.org/",
)
