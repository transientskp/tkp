"""

.. moduleauthor:: TKP <discovery@transientskp.org>
copyright 2011, LOFAR Transients Key Project


The TKP package contains python modules used by the LOFAR Transients
Key Project. These modules perform operations necessary to:

- extract sources from (radio) images
- store these sources in a database
- match sources with cataloged sources
- detect variable sources
- classify variable sources


The division in subpackages follows these steps roughly:

- sourcefinder routines
- database routines (storage, association, variable detection)
- classification routines
- utility routines

"""

__version__ = "2.0-pre"
