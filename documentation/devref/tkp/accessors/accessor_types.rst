======================
Data Accessor Variants
======================

Basic data accessors
++++++++++++++++++++

.. module:: tkp.accessors.dataaccessor

.. autoclass:: tkp.accessors.dataaccessor.DataAccessor
   :members:

The following acessors are derived from the basic :class:`DataAccessor` class:

.. module:: tkp.accessors.fitsimage

.. class:: tkp.accessors.fitsimage.FitsImage

   Generic FITS data access.

.. module:: tkp.accessors.casaimage

.. class:: tkp.accessors.casaimage.CasaImage

   Generic CASA image access.

.. module:: tkp.accessors.kat7casaimage

.. class:: tkp.accessors.kat7casaimage.Kat7CasaImage

   KAT-7 specific CASA image access.

LOFAR-specific data accessors
++++++++++++++++++++++++++++++++++

.. module:: tkp.accessors.lofaraccessor

.. autoclass:: tkp.accessors.lofaraccessor.LofarAccessor
   :members:

The following accessors are derived from the generic :class:`LofarAccessor`:

.. module:: tkp.accessors.lofarfitsimage

.. class:: tkp.accessors.lofarfitsimage.LofarFitsImage

   LOFAR FITS access.

.. module:: tkp.accessors.lofarcasaimage

.. class:: tkp.accessors.lofarcasaimage.LofarCasaImage

   LOFAR CASA image access.
