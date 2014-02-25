#!/usr/bin/env python

import os
from distutils.core import setup
from distutils.command.install import INSTALL_SCHEMES

tkp_scripts = [
    "tkp/bin/pyse.py",
    "tkp/bin/tkp-manage.py",
    "tkp/bin/tkp-inject.py",

    ]


def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)

# Tell distutils not to put the data_files in platform-specific installation
# locations. See here for an explanation:
# http://groups.google.com/group/comp.lang.python/browse_thread/thread/35ec7b2fed36eaec/2105ee4d9e8042cb
for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']

tkp_packages = []
tkp_data_files = []
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)

for dirpath, dirnames, filenames in os.walk('tkp'):
    # Ignore dirnames that start with '.'
    dirnames[:] = [d for d in dirnames if not d.startswith('.') and d != '__pycache__']
    if '__init__.py' in filenames:
        tkp_packages.append('.'.join(fullsplit(dirpath)))
    elif filenames:
        tkp_data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])

setup(
    name = "tkp",
    version = "1.1",
    packages = tkp_packages,
    scripts = tkp_scripts,
    data_files=tkp_data_files,
    description = "LOFAR Transients Key Project (TKP)",
    author = "TKP Discovery WG",
    author_email = "discovery@transientskp.org",
    url = "http://www.transientskp.org/",
)

