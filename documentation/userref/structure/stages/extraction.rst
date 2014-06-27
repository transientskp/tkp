.. _stage-extraction:

=========================
"Blind" source extraction
=========================

A source finding and measurement step is run on the image.  For more details
on the procedure employed, the reader is referred to :ref:`Spreeuw (2010)
<spreeuw-2010>`. Here, we present only a brief introduction.

The algorithm employed is:

#. The image is divided into a square grid of user defined size.

#. Within each cell, the data is sigma-clipped to remove the effect of
   bright sources.

#. The median pixel value within each clipped cell is calculated, and
   interpolated across the image to form a background map.

#. The RMS pixel value within each clipped cell is calculated, and interpolated
   across the image to form a noise map.

#. The background map is subtracted from the data.

#. Pixels in the image data which are more than a "detection threshold" times
   the value of the noise map at the pixel position are identified as sources.

#. Pixels in the image data which are adjacent to source pixels and which more
   than an "analysis threshold" times the value of the noise map at the pixel
   position are appended to the source pixels.

#. The source pixel groups are (optionally) "deblended": multi-component
   sources are split into their constituent parts by a multi-thresholding
   technique.

#. An estimate of the source parameters are made based on the source pixels.
   The barycentre is taken as the position of the source, and the moments about
   that centre are used to estimate axis lengths and position angles.

#. A least squares fit of an elliptical Gaussian to the pixel values is
   performed, starting with the estimated source parameters. If the fit
   converges, the fitted values are returned as the source measurement; if not,
   we return the earlier estimate together with an appropriate flag.

For each source, the following measurements are stored:

* Position (RA and declination, including uncertainties);

* An estimate of the absolute on sky angular error on the position (NB this is
  *not* equivalent to the errors on RA and/or declination);

* The peak flux value;

* The integrated flux value;

* The lengths of the major and minor axes;

* The position angle, measured counterclockwise from the Y axis;

* The significance of the detection (that is, the ratio of the peak flux value
  to the RMS map at that point).

After the blind extraction has been performed, the list of source measurements
is stored in the database.

The following parameters may be configured in the :ref:`job configuration file
<job_params_cfg>`:

Section ``source_extraction``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``detection_threshold``
   Float. The detection threshold as a multiple of the RMS noise.

``analysis_threshold``
   Float. The analysis threshold as a multiple of the RMS noise.

``back_size_x``, ``back_size_y``
   Integers. The size of the background grid parallel to the X and Y axes of
   the pixel grid.

``margin``
   Integer. Pixel data within ``margin`` pixels of the edge of the image will
   be excluded from the analysis.

``extraction_radius_pix``
   Integer. Pixel data more than ``extraction_radius_pix`` pixels from the
   centre of the image will be excluded from the analysis.

``deblend_nthresh``
   Integer. The number of subthresholds to use for deblending. Set to ``0`` to
   disable deblending.

``force_beam``
   Boolean. If ``True``, all detected sources are assumed to have the size and
   shape of the restoring beam (ie, to be unresolved point sources), and these
   parameters are held constant during fitting. If ``False``, all parameters
   are allowed to vary freely.
