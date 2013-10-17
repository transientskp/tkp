.. _tkp-inject:

========================
Image Metadata Injection
========================

Preamble
--------

In order to images through the Trap, they are required to provide a
comprehensive set of metadata, including details such as observation time,
frequency and the shape of the restoring beam.

Unfortunately, not all images are produced with all the required metadata
embedded. The metadata injection tool, ``tkp-inject.py``, makes it possible to
annotate images with a user-supplied set of metadata. This can be used to
either replace incorrect metadata provided with an image, or to provide it
from scratch.


Configuration
-------------

``tkp-inject.py`` is configured by means of a :mod:`ConfigParser` format file
named ``inject.cfg`` in the users job directory. See the documentation on
:ref:`pipeline configuration <config-overview>` for details.

The default ``inject.cfg`` file contains the following settings:

.. literalinclude:: /../tkp/conf/job_template/inject.cfg

Any or all of these may be changed by the user to reflect their requirements.
