.. _pyse:

====
PySE
====

Preamble
--------

This document briefly describes the means by which the Transients Project
source extraction & measurement code (henceforth ``pyse.py``) may be used to
obtain a list of sources found in a collection of images stored as FITS files.
It does not attempt to act as a complete reference to the TKP codebase.

Introduction
------------

Pyse provides the following capabilities:

- Identification of sources in astronomical images:

  - By a simple thresholding technique (ie, locating contiguous islands of
    pixels above some multiple of the noise in the image), or

  - By making use of a False Detection Rate (FDR) algorithm (`Hopkins et al.,
    AJ, 123, 1086, 2002
    <http://adsabs.harvard.edu/abs/2002AJ....123.1086H>`_).

- Deblending merged sources.

- Quick estimation of source properties based on the calculation of moments.

- Fitting of identified sources with elliptical Gaussians for accurate
  measurement of source properties.

- All measurements made are accompanied by a comprehensive error analysis.

For details of all algorithms implemented, the reader is referred to the PhD
thesis by `Spreeuw <http://dare.uva.nl/en/record/340633>`_ (University of
Amsterdam, 2010).

It is worth emphasizing that there are a number of differences compared to
projects such as, for example, BDSM. In particular, the ``pyse.py`` code is made
available in the form or Python modules, primarily designed for integration
into a pipeline or other script, rather than for use as an interactive
analysis environment. Further, it is reasonable to assume that astronomical
transients are unresolved, so the code does not attempt to decompose complex,
extended sources into a multiple component model.

Command Line Usage
------------------

A script is available to make it possible to test the basic functionality of
the ``pyse.py`` code. It does not make all the features listed above available.

Assuming ``pyse.py`` exists on your ``$PATH``, it is involed by simply providing
a list of filenames::

  $ pyse.py file1.fits ... fileN.fits

For each file specified, a list of sources identified is printed to the
screen.

A list of available command line option may be obtained with the
``-h``/``--help`` option:

.. program-output:: python ../tkp/bin/pyse.py -h

By default, source extraction is carried out by thresholding: that is,
identifying islands of pixels which exceed a particular multiple of the RMS
noise. In this mode, the following two parameters are may be supplied:

The ``--detection`` argument specifies the multiple of the RMS noise which is
required for detection; ie, setting ``--detection=5`` is equivalent to
requiring pixels used for detecting sources to be at 5 sigma.

The ``--analysis`` argument specifies the significance level used when
performing fitting. It should be lower than ``--detection``, such that once
islands have been identified a larger number of pixels is included for the
fitting process.

However, if the ``--fdr`` option is given, a False Detection Rate algorithm is
used instead. In this case, an additional ``--alpha`` argument may be given to
specify the :math:`\alpha` parameter (as defined by `Hopkins
<http://adsabs.harvard.edu/abs/2002AJ....123.1086H>`_).

*Note* that if ``--fdr`` is specified, any values given for ``--detection``
and ``--analysis`` are *not used*. Conversely, if ``--fdr`` is not specified,
any value given for ``--alpha`` is *not used*.

If the ``--regions`` option is specified, a DS9-compatible region file is
output showing the shapes & positions of the sources. It is named according to
the input filename with the extension changed to ``.reg``.

If the ``--residuals`` option is specified, a FITS file is produced showing
the residuals left after the fitted sources have been subtraced from the input
image. It is named according to the input filename with ``.residuals``
inserted before the extension.

If the ``--islands`` option is specified, a FITS file is produced showing the
Gaussians which have been fitted in the data. It is named according to the
input filename with ``.islands`` inserted before the extension. The sum of
this file with that produced by ``--residuals`` above should total the input
image.

If the ``--skymodel`` option is given, a skymodel file suitable for use with
BBS will be generated. It is named according to the input filename with the
extension changed to ``.skymodel``.

If the ``--csv`` option is given, a comma-separated list of sources will be
written to file. It is named according to the input filename with the
extension changed to ``.csv``.

If the ``--rmsmap`` option is given, a FITS file is produced showing the noise
map which has been generated during the source-finding process. It is named
according to the input filename with ``.rms`` inserted before the extension.

If the ``--sigmap`` option is given, a FITS file is produced showing the
significance of each pixel: that is, the background-subtracted image pixel
value divided by the RMS noise at that pixel. It is named according to the
input filename with ``.sigmap`` inserted before the extension.

If the ``--deblend`` option is specified, ``pyse.py`` will attempt to separate
composite sources into multiple components and fit each one independently. The
number of subthresholds used in this process can be specified using the
``--deblend-thresholds`` argument. Refer to Spreeuw's thesis for a detailed
description of the algorithm used.

``--bmaj``, ``--bmin`` and ``--bpa`` specify the shape of the restoring beam.
They are equivalent to the ``BMAJ``, ``BMIN`` and ``BPA`` FITS headers.
Normally, the code will read the beam shape from the image metadata; however,
if it is not available, it must be manually specified using these arguments or
the process will abort.

When generating background and RMS maps of the image prior to source
detection, it is segmented into a grid. The size of the grid can be specified
using the ``--grid`` option. The optimal value is a compromise: it should be
significantly larger than the most extended sources in the image, but small
enough to account for small-scale variation across the image.

Sometimes, it is useful to exclude the edge regions of an image from
processing. The ``--margin`` takes an argument given in pixels and masks off
all portions of the image within the given distance of the edge before
processing. The ``--radius`` argument is similar, but rather masks off all
parts of the image more than the given distance from the centre. This options
are cumulative.

If the ``--force-beam`` option is given, PySE will insist that all sources
have axis lengths and position angles equal to the restoring beam parameters.
This is (might be...) a good assumption if you are observing only point
sources.

If the ``--detection-image`` option is specified, PySE will identify sources
and the positions of pixels which comprise them on the deteciton image, but
then use the corresponding pixels on the target images to perform
measurements. Of course, the detection image and the target image(s) must have
the same pixel dimensions. Note that only a single detection image may be
specified, and the same pixels are then used on all target images. Note
further that this ``--detection-image`` option is incompatible with ``--fdr``.

It is possible to configure PySE to perform a fit to user-specified positions
in the image _rather_ than "blindly" locating sources and attempting to fit
them. (Note that it is not possible to do both at once: that requires invoking
PySE twice.) This mode may be invoked either by using either of the
``--fixed-posns`` or ``--fixed-posn-file`` options. The former directly reads a
list of positions from the command line; the latter accepts a filename, and
reads the positions to fit from that. In both cases, the positions themselves
are provided in `JSON <http://json.org/>`_ format, and should consist of a
_list_ of RA, declination _pairs_ given in decimal degrees.

When fitting to a fixed position, a square "box" of pixels is chosen around
the requested position, and the optimization procedure allows the source
position to vary within that box. The size of the box may be changed with the
``--ffbox`` option. Note that this parameter is given in units of the major
axis of the beam.

All of these arguments are optional (with the caveat that the beam shape must
be provided if not included with the image).

Output Definition
-----------------

The Gaussian fitted to sources is defined as:

.. math::

   peak * \exp(\ln(2.0) * ((x \cos(\theta) + y \sin(\theta)) / semiminor)^2 + ((y \cos(\theta) - x \sin(\theta)) / semimajor)^2)

In other words:

- :math:`x` and :math:`y` are the Cartesian coordinates of the centre of the Gaussian;

- :math:`peak` is the value at the centre of the Gaussian;

- :math:`theta` is the position angle of the major axis measured counterclockwise
  from the y axis;

- :math:`semimajor` and :math:`semiminor` are the half-widths at half-maximum of the
  Gaussian along its major and minor axes, respectively.
