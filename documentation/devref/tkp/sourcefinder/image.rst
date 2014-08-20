.. _sourcefinder-image:

+++++++++++++++++++++++++++++++++++++++++++++++++++++++
:mod:`tkp.sourcefinder.image` -- Image class & routines
+++++++++++++++++++++++++++++++++++++++++++++++++++++++

This module provides simple access to an image, without database
overhead. The Image class handles the actual data (a (2D) numpy
array), the world coordinate system (a tkp.utility.coordinates.WCS
instance) and the beam information. While these three objects are
supplied upon instantiation of an Image, one can use a
:class:`tkp.accessors.dataaccessor.DataAccessor` object to automatically
derive these from the image file itself (provided the header
information in the file is correct).
 
.. automodule:: tkp.sourcefinder.image
   :synopsis: Sourcefinder Image class and routines for simple image handling
   :members:
