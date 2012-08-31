Installtion
===========
This is now build with numpy.distutils from the TKP root.

Readme
======

This directory contains the AIPS deconv routine (deconv.f), that
deconvolves two 2D Gaussians.  The routine is converted to a compiled
Python module with the use of f2py: deconv.so

Since this is a straightforward routine, it seemed interesting to at
least try and rewrite the routine directly into Python (there does not
appear to exist such a routine in numpy/scipy/ndimage or the like,
probably because it is too specific). The result can be found as
deconv2.py.

This rewrite revealed a few issues with the routine:

- The FORTRAN routine compares REAL .eq. 0.0, instead of doing
  something like ABS(REAL) .lt. PRECISION, which would account for
  rounding errors. In some specific circumstances, these round-off
  errors can tip the scales in a significant manner: the ELSE part of
  the corresponding IF statement is picked, which then happens to
  divide one small number by another small number (which should be
  prevented by a correct comparison).

  The Python code therefore reads `if abs(rhoc) < precision:`.

- The use of REALs showed the rounding errors to make a significant
  difference when compared to the Python code: the latter internally
  uses double precision (differences are for example 2.5 versus 2.3 as
  result, roughly a 10% difference). Changing the REALs to DOUBLE
  PRECISIONs made this difference disappear.

The Python code also leaves out a few unnecessary modulo statements
(which are relatively computationally intensive). And the Python code
raises exceptions, instead of setting ierr(or) to > 0.

The Python code does maintain the same API, ie, the same calling code;
a possible change could be to accept the two beams as 3-tuples instead
of 6 separate parameters.

The script `deconv_test.py` tests both the accuracy of the two
routines and compares their speed: the Python code currently runs
about 7.5 times slower. One should also notice the 45 degrees
difference in one of the outcomes: the result of replacing `== 0` with
`abs() < precision`.



For the record, this exercise turned up some interesting routine in
the USG repository:
http://usg.lofar.org/svn/code/trunk/src/Anaamika/scripts/functions.py
. This module contains a deconv() routine, which is a similar rewrite
of the AIPS tasks. And thus has the same problems as mentioned
above. In addition, because of missing parentheses and operator
precedence, the modulo operations are incorrect (as of March 9, 2011).
(Note that the code also sets an error variable, which is then happily
ignored).

The exact same routine can also be found in
http://usg.lofar.org/svn/code/trunk/src/Anaamika/scripts/compute.py .
