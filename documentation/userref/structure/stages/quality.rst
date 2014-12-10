.. _stage-quality:

===================
Quality check stage
===================
(See also the :ref:`relevant configuration parameters<job_params_quality>`.)

Images are checked to ensure they meet a minimum "quality" standard such that
useful scientific information can be extracted from them. If an image fails to
meet quality standards, it is rejected and not included in further processing.
However, it is still recorded in the database for book-keeping purposes.

The quality check code is structured such that different sets of tests can be
applied to images from different telescopes
(see source of the :py:func:`tkp.steps.quality.reject_check` function for
implementation details).
Currently, only a selection of
tests designed to process LOFAR images are available. Three separate tests are
performed:

Image RMS
---------
The central subsection of the image is iteratively sigma-clipped
until it reaches a user-defined convergence. The RMS of the clipped value is
compared to the theoretically expected image noise based on the LOFAR
configuration in use. The image is rejected if the noise is signifcantly
greated than expected.



Beam shape
----------
The restoring beam is represented as an ellipse, parameterized by lengths of
its major and minor axes and a position angle. These parameters are checked
for sanity. Four separate checks are applied:

* None of the beam parameters should be infinite.
* Both beam axes should be at least two pixels long (the beam is not
  undersampled).
* Neither beam axis should be longer than a user-defined threshold (the beam
  is not oversampled).
* The ratio of the major to the minor axis should be lower than a user defined
  threshold (the beam is not excessively elliptical).


Nearby bright sources
---------------------
There should be no bright radio sources within a user-defined radius of the
image centre. The sources checked for are:

* Cassiopeia A
* Cygnus A
* Tauraus A
* Hercules A
* Virgo A
* The Sun
* Jupiter




