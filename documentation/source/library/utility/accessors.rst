.. _utility-accessors:

+++++++++++++++++++++++++++++++++++++++++++++++++++++++
:mod:`tkp.utility.accessors` -- Image container classes
+++++++++++++++++++++++++++++++++++++++++++++++++++++++
.. |last_updated| last_updated::

*This document last updated:* |last_updated|.

Introduction
------------

The "accessors" system attempts to abstract away the physical image storage
format from the library logic. The higher-level data access routines should
not care whether the data is stored in a CASA table, or a FITS file, or in
some other format: they should be coded against a uniform interface provided
by the appropriate accessor.

An accessor should subclass
:class:`tkp.utility.accessors.dataaccessor.DataAccessor`, and must provide
the following attributes:

.. warning::

    This list is currently incomplete.

``beam``
    Restoring beam. Tuple of three floats: semi-major axis (in pixels),
    semi-minor axis (pixels) and position angle (radians).

``data``
    NumPy array providing access to the (two-dimensional) pixel data.

``centre_ra``
    Right ascension at the central point of the image, in decimal degrees.

``centre_dec``
    Declination at the central point of the image, in decimal degrees.

``wcs``
    An instance of :class:`tkp.utility.coordinates.WCS`, appropriately
    initialized to handle coordinate conversions for this image.

API Documentation
-----------------

.. automodule:: tkp.utility.accessors
   :synopsis: Accessor (image container) classes
   :members:
