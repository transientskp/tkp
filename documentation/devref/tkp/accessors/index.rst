.. _accessors:

+++++++++++++++++++++++++++++++++++++++++++++++
:mod:`tkp.accessors` -- Image container classes
+++++++++++++++++++++++++++++++++++++++++++++++

Introduction
------------

The "accessors" system attempts to abstract away the physical image storage
format from the library logic. The higher-level data access routines should
not care whether the data is stored in a CASA table, or a FITS file, or in
some other format: they should be coded against a uniform interface provided
by the appropriate accessor.

An accessor should subclass
:class:`tkp.accessors.dataaccessor.DataAccessor`, which is an abstract
base class. Accessors *must* conform to the DataAccessor interface by
defining the relevant attributes (see the attributes listed under
:class:`tkp.accessors.dataaccessor.DataAccessor` for full details).
An accessor which provides all of these attributes is guaranteed to be usable
with all core TraP functionality.

In some cases, most notably :ref:`quality control <quality>`, specialized (eg,
per-telescope) metadata may also be required. A further abstract base class
should be constructed to define the interface required. For example,
:class:`tkp.accessors.lofaraccessor.LofarAccessor` defines the following
metadata which must be provided for LOFAR quality control:

``antenna_set``
   Antenna set in use during observation. String; ``LBA_INNER``, ``LBA_OUTER``,
   ``LBA_SPARSE``, ``LBA`` or ``HBA``

``ncore``
   Number of core stations in use during observations constituting this image.
   Integer.

``nremote``
   Number of remote stations in use during observations constituting this
   image. Integer.

``nintl``
   Number of international stations in use during observations constituting
   this image. Integer.

``subbandwidth``
    Width of a subband, in Hz.

``subbands``
    Number of subbands.


API Documentation
-----------------

.. toctree::
   api
   accessor_types
