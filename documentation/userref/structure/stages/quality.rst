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

Quality checks are performed on all fits images input into TraP. Two
key tests are performed.


Image RMS
---------
The central subsection of the image is iteratively sigma-clipped
until it reaches a user-defined convergence giving the rms of the
clipped region.

The rms is first compared to the globally acceptable minimum and
maximum rms values as defined in the job_params.cfg file.

Once sufficient images have been processed (given by rms_est_history
in the job_params.cfg file), the rms values for all the images are
fitted using a Gaussian distribution. The rms value of the
new image is then compared to the allowed sigma deviation
(rms_rej_sigma) from this Gaussian distribution.

The image is rejected if the noise is signifcantly
greated or less than expected.


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



