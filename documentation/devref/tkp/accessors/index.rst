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
base class (ie, it has :class:`abc.ABCMeta` as its metaclass). Accessors
*must* conform to the DataAccessor interface. This means they must provide the
following attributes:

``beam``
    Restoring beam. Tuple of three floats: semi-major axis (in pixels),
    semi-minor axis (pixels) and position angle (radians).

``centre_ra``
    Right ascension at the central point of the image, in decimal degrees.

``centre_dec``
    Declination at the central point of the image, in decimal degrees.

``data``
    NumPy array providing access to the (two-dimensional) pixel data.

``freq_bw``
   The frequency bandwidth of the image, in Hz.

``freq_eff``
   Effective frequency of the image in Hz. That is, the mean frequency of
   all the visibility data which comprises this image.

``pixelsize``
   (x, y) tuple representing the size of a pixel along each axis in units
   of degrees.

``tau_time``
   Total time on sky, in seconds.

``taustart_ts``
   Timestamp of the first integration which constitutes part of this
   image. MJD in seconds.

``url``
   A (string) URL representing the location of the image at time of
   processing.

``wcs``
    An instance of :class:`tkp.utility.coordinates.WCS`, appropriately
    initialized to handle coordinate conversions for this image.

An accessor which provides all of these properties is guaranteed to be usable
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
