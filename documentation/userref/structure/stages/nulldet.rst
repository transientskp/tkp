.. _stage-nulldet:

=======================
Null detection handling
=======================

A "null detection" is the term used to describe a source which was expected to
be measured in a particular image (because it has been observed in previous
images covering the same field of view) but was in fact not detected by the
:ref:`blind extraction <stage-extraction>` step.

After the blindly-extracted source measurements have been stored to the
database, we retrieve from the database a list of all sources which are fall
within the field of view of the image being processed but which could never be
associated with any of the blindly-extracted source measurements made. The
logic for this check is as follows.

We define a "dimensionless distance" :math:`r_{ij}` between two sources
:math:`r_i` and :math:`r_j` with RA :math:`\alpha` and declination
:math:`\delta` as:

.. math::

  r_{ij} = \sqrt{
     \frac{(\Delta \alpha)^{2}_{ij}}{\sigma^2_{\Delta \alpha, ij}} +
     \frac{(\Delta \delta)^{2}_{ij}}{\sigma^2_{\Delta \delta, ij}}
  }

where :math:`\sigma` indicates a one sigma RMS uncertainty,

.. math::

  \sigma^2_{\Delta \alpha, ij} = \sigma^2_{\alpha, i} + \sigma^2_{\alpha, j}

and :math:`\sigma^2_{\Delta \delta, ij}` is defined analagously
(:ref:`Scheers, 2011 <scheers-2011>`). We then check for all known sources for
which the dimensionless distance to all blind extractions is greater than some
user-defined threshold: these sources are our null detections.

For all sources identified as null detections, we measure fluxes by performing
a forced elliptical Gaussian fit to the expected source position on the image.
The procedure followed is similar to that used for :ref:`blind extraction
<stage-extraction>`, but rather than allowing the pixel position of the
barycentre to vary freely, it is held to the known source position. No
deblending is performed.

The results of these "forced" source measurements are marked as such and
appended to the database.

It is worth emphasizing that the above procedure does *not* guarantee that
every known source will have either a blind detection or a forced-fit
measurement in every image. In particular, the above logic checks that a
source association is possible, not that one will actually take place. The
:ref:`full association procedure <stage-association>` is more complex than the
check included here, and it is possible that there will remain catalogued
sources with no associated measurement for the image.

The following parameters may be configured in the :ref:`job configuration file
<job_params_cfg>`:

Section ``association``
^^^^^^^^^^^^^^^^^^^^^^^

``deruiter_radius``
   Float. The maximum dimensionless distance within which source association
   is possible.

Section ``source_extraction``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``backsize_x``, ``backsize_y``, ``margin``, ``extraction_radius_pix``, ``max_degredation``, ``force_beam``
   Defined as for :ref:`blind extraction <stage-extraction>`.
