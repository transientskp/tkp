#
# LOFAR Transients Key Project
#
# Pipeline configuration module. This file holds configurable settings for
# all the constituent modules in tkp.
#

import numpy
import os
from scipy import integrate as integr

#
# TESTING
#
# Data files for testing should be available under this path
from tkp.tests import __path__ as testpath
datapath = os.path.join(testpath[0], "data")

#
# DATABASE SETTINGS
#
# If True, attempt to interact with a database.
# The database is used not merely for storing results, but also for generating
# ID numbers for various objects.
# If database_enabled = True, UUIDs will be used instead of database IDs.
database_enabled = True

#database_type = "MySQL"
database_type = "MonetDB"

# The following settings are ignored if database_enabled = True.
database_host = "ldb001"
database_user = "tkp"
database_passwd = "tbw"
#database_user = "lofar"
#database_passwd = "cs1"
if database_type == "MonetDB":
    database_lang = "sql"
else:
    database_lang = ""
database_port = 50000

# This turns on database tests using the unittest framework. These only make
# sense if you're running on a machine which has a locally available (ie, with
# the "mysql" binary) and configured MySQL installation.
database_test = False

if not database_enabled:
    database_test = False

if database_test:
    database_dbase = "pipeline_test"
else:
    #database_dbase = "pipeline_develop"
    database_dbase = "pipeline_tkp"


# Source association constants
DERUITER_R = 0.0010325


# BACKGROUND & RMS MAP SETTINGS
#
# Background sizes. These are used in generating background maps.
# Should be a compromise: substantially bigger than the sources you expect to
# detect, but small enough that we don't miss local variations in background.
# It's not strictly required by the code for them to be factors of the overall
# map dimensions, but, if they aren't, the edges of the maps are computed
# based on potentially small number statistics.
BACK_SIZEX = 32
BACK_SIZEY = 32

# Apply a median filter of this size to the background and RMS grids. Settings
# this to '0' or 'False' disables the filtering. Note that '1' leaves the data
# unchanged, so you're just burning CPU cycles...
median_filter = 0

# This limits median filtering to only occuring when the calculated background
# or RMS differs from the median by an amount exceeding the threshold. Set it
# to '0' or 'False' to disable the threshold for a (slight) speedup. This is
# the equivalent of the BACK_FILTERTHRESH parameter in SExtractor.
mf_threshold = 0

# Order of the spline interpolation to be used when generating
# background/RMS/FDR maps. interpolate_order=1 (bilinear interpolation) guarantees no negative
# rms noise values if the grid values are positive, i.e. always.
# Splines have interpolate_order=3 and do not provide this safeguard.
interpolate_order = 1

#
# GENERAL IMAGE HANDLING
#
# Set a margin. This is a number of pixels around the edge of the image that
# will be masked off and not used in calculations, thereby avoiding edge
# effects. Set to 0 to disable.
margin = 0

# Window of reliability. Hanno's explanation:
#
# This code calculates a window within a FITS image that is "reliable", i.e.
# the mapping from pixel coordinates to celestial coordinates is well defined.
# Often this window equals the entire FITS image, in some cases, e.g.,in
# all-sky maps, this is not the case.  So there is some user-allowed maximum
# degradation.
#
# The degradation of the accuracy of astrometry due to projection effects at a
# position on the sky phi radians away from the center of the projection is
# equal to 1/cos(phi).  So if you allow for a maximum degradation of 10% the
# code will output pixels within a circle with a radius of
# arccos(1./(1.+0.1))=24.6 degrees around the center of the projection. The
# output FITS image will be the largest possible square within that circle.
#
# I assume that we are working with SIN projected images.  So in the east-west
# direction (M=0) the pixel that is max_angle away from the center of the SIN
# projection is self.centrerapix+sin(max_angle)/raincr_rad In the north-south
# direction (L=0) the pixel that is max_angle away from the center of the SIN
# projection is self.centredecpix+sin(max_angle)/decincr_rad Now cutting out
# the largest possible square is relatively straightforward.  Just multiply
# both of these pixel offsets by 0.5*sqrt(2.).  See "Non-Linear Coordinate
# Systems in AIPS" at
# ftp://ftp.aoc.nrao.edu/pub/software/aips/TEXT/PUBL/AIPSMEMO27.PS, paragraph
# 3.2, for details on SIN projection.
#
# Here, we set the user-defined max degredation (as a fraction; set to False to
# disable).
max_degradation = 0.2

#
# CLASSIFIER SETTINGS
#
# What methods do we call to assemble a 'feature vector' from a lightcurve?
featureVector = ("meanFlux",)

#
# SEXRACTION SETTINGS

# FDR parameters
# "The FDR procedure... guarantees that <FDR> \le \alpha"
# Where <FDR> is the number of incorrectly-detected pixels divided by the
# total number of detected pixels.
fdr_alpha = 1e-2

# "Traditional" RMS thresholding parameters
# Structuring element
structuring_element = [[0,1,0], [1,1,1], [0,1,0]]
# Should we deblend? It makes the whole process more complicated and fragile.
deblend = False
# Difference (in terms of fractional rms) between subthresholds.
# subthrdiff has been deprecated and replaced by deblend_nthresh, like in SExtractor.
deblend_nthresh=32
# This parameter is used for deblending. It sets a significance criterion for subislands, to avoid picking up
# noise, equivalent to SExtractor, see the manual, section 6.4 (deblending).
deblend_mincont=0.005
# Select islands based on this sigma
detection_threshold = 10.0
# Include anything above this many sigma in fitting
analysis_threshold = 3.0
# Should we calculate residual maps?
# If this is true, we should end up with two extra attributes for the
# ImageData object after source extraction: residuals_from_deblending and
# residuals_from_Gauss_fitting.
residuals = True


# In order to derive the error bars from Gauss fitting from the Condon (1997)
# formulae one needs the so called correlation length. The Condon formulae
# assume a circular area with diameter theta_N (in pixels) for the correlation. This was later generalized by
# Hopkins et al. (AJ 125, 465 (2003)) for correlation areas which are not axisymmetric.
# Basically one has theta_N**2=theta_B*theta_b.
# theta_B=2.*semimaj and theta_b=2.*semimin are good estimates in general.
def calculate_correlation_lengths(semimajor,semiminor):
    corlengthlong=2.*semimajor
    corlengthshort=2.*semiminor
    return corlengthlong,corlengthshort

alpha_maj1=2.5
alpha_min1=0.5
alpha_maj2=0.5
alpha_min2=2.5
alpha_maj3=1.5
alpha_min3=1.5
clean_bias=0.0
clean_bias_error=0.0
frac_flux_cal_error=0.0

def calculate_beamsize(semimajor,semiminor):
    beamsize=numpy.pi*semimajor*semiminor
    return beamsize

# The position calibration errors need to be included due to the rms offsets
# (See also Condon et al.(1998).
# For now we set them to 0.
eps_ra = 0.
eps_dec = 0.

# Previously, we adopted Rengelink's correction for the underestimate of the peak of the Gaussian
# by the maximum pixel method: fudge_max_pix=1.06. See the WENSS paper (1997A&AS..124..259R) or his thesis.
# (The peak of the Gaussian is, of course, never at the exact center of the pixel, that's why the maximum pixel
# method will always underestimate it.)
# But, instead of just taking 1.06 one can make an estimate of the overall correction by assuming that the true peak
# is at a random position on the peak pixel and averaging over all possible corrections.
# This overall correction makes use of the beamshape, so strictly speaking only accurate for unresolved sources.
def fudge_max_pix(semimajor,semiminor,theta):
     correction=integr.dblquad(lambda y, x: numpy.exp(numpy.log(2.)*\
     (((numpy.cos(theta)*x+numpy.sin(theta)*y)/semiminor)**2.+\
     ((numpy.cos(theta)*y-numpy.sin(theta)*x)/semimajor)**2.)),-0.5,0.5,lambda ymin:-0.5, lambda ymax:0.5)[0]
     return correction
# When we use the maximum pixel method, with a correction fudge_max_pix, there should be no bias, unless the peaks of the Gaussians
# are not randomly distributed, but relatively close to the centres of the pixels due to selection effects from detection thresholds.
# Disregarding the latter effect and noise, we can compute the variance of the maximum pixel method by integrating (the true flux-
# the average true flux)**2=(the true flux-fudge_max_pix)**2 over the pixel area and dividing by the pixel area (=1).
# This is just equal to integral of the true flux **2 over the pixel area - fudge_max_pix**2.
def maximum_pixel_method_variance(semimajor,semiminor,theta):
     variance=integr.dblquad(lambda y, x: numpy.exp(2.*numpy.log(2.)*\
     (((numpy.cos(theta)*x+numpy.sin(theta)*y)/semiminor)**2.+\
     ((numpy.cos(theta)*y-numpy.sin(theta)*x)/semimajor)**2.)),-0.5,0.5,lambda ymin:-0.5, lambda ymax:0.5)[0]\
     -fudge_max_pix(semimajor,semiminor,theta)**2
     return variance
