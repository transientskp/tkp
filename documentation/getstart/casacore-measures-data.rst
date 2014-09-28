.. _casacore-measures:

Configuring the casacore ephemeris
==================================

Note that as part of the installation you (or your system administrator) will
have installed the casacore "measures data". This includes information
essential to carrying out astronomical calculations, such as a list of leap
seconds and a set of solar system ephemerides (which specify the positions of
the planets at any given time). Data for the ephemerides are ultimately
supplied by `NASA JPL`_; they have been converted into a format that casacore
can use. Any given ephemeris is only valid for a limited time (usually on the
order of centuries), determined by the accuracy with which it was calculated.

By default, casacore will use the ``DE 200`` ephemeris. Although the version
of ``DE 200`` supplied by JPL is valid until 2169, *some versions converted
for use with casacore are not*, and may not provide coverage of the dates of
your observation. A simple Python script can be used to check::

  $ cat check_ephemeris.py
  import sys
  from  pyrap.measures import measures
  dm = measures()
  dm.do_frame(dm.epoch('UTC', sys.argv[1]))
  dm.separation(dm.direction('SUN'), dm.direction('SUN'))
  $ python check_ephemeris.py 1990/01/01
  $ python check_ephemeris.py 2015/01/01
  WARN    MeasTable::Planetary(MeasTable::Types, Double)
    (file /build/buildd/casacore-1.7.0/measures/Measures/MeasTable.cc, line 4056)
    Cannot find the planetary data for MeasJPL object number 3 at UT day 57023 in
    table DE200

If no warning is printed, there is no problem; otherwise, you should use a
different ephemeris. For example, the ``DE 405`` ephemeris should be valid
until at least early 2015::

  $ cat > ~/.casarc
  measures.jpl.ephemeris: DE405
  $ python check_ephemeris.py 2015/01/01
  # No warnings

An alternative issue sometimes encountered is that of measures data which is
simply outdated.
Should you see an error along the lines of ::

  SEVERE  gaincal::MeasTable::dUTC(Double) (file measures/Measures/MeasTable.cc, line 6307    Leap second table TAI_UTC seems out-of-date.
  SEVERE  gaincal::MeasTable::dUTC(Double) (file measures/Measures/MeasTable.cc, line 6307)+  Until table is updated (see aips++ manager) times and coordinates
  SEVERE  gaincal::MeasTable::dUTC(Double) (file measures/Measures/MeasTable.cc, line 6307)+  derived from UTC could be wrong by 1s or more

Then you might try to update your measures data via Rsync, as described in
`this NRAO helpdesk article <NRAO_article_>`_

.. _NASA JPL: http://iau-comm4.jpl.nasa.gov/README.html
.. _NRAO_article: http://casaguides.nrao.edu/index.php?title=Fixing_out_of_date_TAI_UTC_tables_%28missing_information_on_leap_seconds%29
