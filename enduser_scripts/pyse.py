"""
Simple interface to TKP source identification & measurement code.
John Sanders & John Swinbank, 2011.

This is a simplified script for running source finding with a minimal set of
arguments. It does not provide a full configuration interface or access to
all features.

Run as:

  $ python pyse.py file ...

For help with command line options:

  $ python pyse.py --help

See chapters 2 & 3 of Spreeuw, PhD Thesis, University of Amsterdam, 2010,
<http://dare.uva.nl/en/record/340633> for details.
"""
import sys
import math
import os.path
from cStringIO import StringIO
from optparse import OptionParser

import pyfits
import numpy

from tkp.utility.accessors import FitsFile
from tkp.utility.accessors import sourcefinder_image_from_accessor
from tkp.utility.accessors import writefits as tkp_writefits

from tkp.sourcefinder.utils import generate_result_maps

def regions(sourcelist):
    """
    Return a string containing a DS9-compatible region file describing all the
    sources in sourcelist.
    """
    output = StringIO()
    print >>output, "# Region file format: DS9 version 4.1"
    print >>output, "global color=green dashlist=8 3 width=1 font=\"helvetica 10 normal\" select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1"
    print >>output, "image"
    for source in sourcelist:
        print >>output, "ellipse(%f, %f, %f, %f, %f)" % (
            source.x.value,
            source.y.value,
            source.smaj.value*2,
            source.smin.value*2,
            math.degrees(source.theta)+90
        )
    return output.getvalue()

def skymodel(sourcelist, ref_freq=73800000):
    """
    Return a string containing a skymodel from the extracted sources for use in self-calibration.
    """
    output = StringIO()
    print >>output, "#(Name, Type, Ra, Dec, I, Q, U, V, MajorAxis, MinorAxis, Orientation, ReferenceFrequency='60e6', SpectralIndex='[0.0]') = format"
    for source in sourcelist:
        print >>output, "%s, GAUSSIAN, %s, %s, %f, 0, 0, 0, %f, %f, %f, %f, [0]" % (
            "ra:%fdec:%f" % (source.ra, source.dec),
            "%fdeg" % (source.ra,),
            "%fdeg" % (source.dec,),
            source.flux,
            source.smaj_asec,
            source.smin_asec,
            source.theta_celes,
            ref_freq
        )
    return output.getvalue()

def csv(sourcelist):
    """
    Return a string containing a csv from the extracted sources.
    """
    output = StringIO()
    print >>output, "ra, ra_err, dec, dec_err, smaj, smaj_err, smin, smin_err, pa, pa_err, int_flux, int_flux_err, pk_flux, pk_flux_err"
    for source in sourcelist:
        print >>output, "%f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f" % (
            source.ra,
            source.ra.error,
            source.dec,
            source.dec.error,
            source.smaj_asec,
            source.smaj_asec.error,
            source.smin_asec,
            source.smin_asec.error,
            source.theta_celes,
            source.theta_celes.error,
            source.flux,
            source.flux.error,
            source.peak,
            source.peak.error,
        )
    return output.getvalue()

def summary(filename, sourcelist):
    """
    Return a string containing a human-readable summary of all sources in
    sourcelist.
    """
    output = StringIO()
    print >>output, "** %s **\n" % (filename)
    for source in sourcelist:
        print >>output, "RA: %s, dec: %s" % (str(source.ra), str(source.dec))
        print >>output, "Semi-major axis (arcsec): %s" % (str(source.smaj_asec))
        print >>output, "Semi-minor axis (arcsec): %s" % (str(source.smin_asec))
        print >>output, "Position angle: %s" % (str(source.theta_celes))
        print >>output, "Flux: %s" % (str(source.flux))
        print >>output, "Peak: %s\n" % (str(source.peak))
    return output.getvalue()

def handle_args():
    """
    Parses command line options & arguments using OptionParser.
    Options & default values for the script are defined herein.
    """
    usage = "usage: %prog [options] file1 ... fileN"
    parser = OptionParser(usage)
    parser.add_option("--fdr", action="store_true", dest="fdr", help="Use False Detection Rate algorithm")
    parser.add_option("--alpha", default=1e-2, type="float", help="FDR Alpha")
    parser.add_option("--detection", default=10, type="float", help="Detection threshold")
    parser.add_option("--analysis", default=3, type="float", help="Analysis threshold")
    parser.add_option("--regions", action="store_true", help="Generate DS9 region file(s)")
    parser.add_option("--residuals", action="store_true", help="Generate residual maps")
    parser.add_option("--islands", action="store_true", help="Generate island maps")
    parser.add_option("--deblend", action="store_true", help="Deblend composite sources")
    parser.add_option("--deblend-thresholds", default=32, type="int", help="Number of deblending subthresholds")
    parser.add_option("--bmaj", type="float", help="Major axis of beam")
    parser.add_option("--bmin", type="float", help="Minor axis of beam")
    parser.add_option("--bpa", type="float", help="Beam position angle")
    parser.add_option("--grid", default=64, type="int", help="Background grid segment size")
    parser.add_option("--margin", default=0, type="int", help="Margin applied to each edge of image (in pixels)")
    parser.add_option("--radius", default=0, type="float", help="Radius of usable portion of image (in pixels)")
    parser.add_option("--skymodel", action="store_true", help="Generate sky model")
    parser.add_option("--csv", action="store_true", help="Generate csv text file for use in programs such as TopCat")
    parser.add_option("--rmsmap", action="store_true", help="Generate RMS map")
    parser.add_option("--sigmap", action="store_true", help="Generate significance map")
    return parser.parse_args()

def set_configuration(options):
    """
    Update the standard sourcefinder configuration based on command line
    arguments.
    Note that tkp.config.config already contains the default configuration
    plus any changes made in the users ~/.tkp.cfg.
    """
    from tkp.config import config
    config = config['source_extraction']
    config['back_sizex'] = options.grid
    config['back_sizey'] = options.grid
    config['margin'] = options.margin
    config['radius'] = options.radius
    config['deblend'] = bool(options.deblend)
    config['deblend_nthresh'] = options.deblend_thresholds
    if options.residuals or options.islands:
        config['residuals'] = True

def writefits(filename, data, header={}):
    try:
        os.unlink(filename)
    except OSError:
        # Thrown if file didn't exist
        pass
    tkp_writefits(data, filename, header)

def run_sourcefinder(files, options):
    """
    Iterate over the list of files, running a sourcefinding step on each in
    turn. If specified, a DS9-compatible region file and/or a FITS file
    showing the residuals after Gaussian fitting are dumped for each file.
    A string containing a human readable list of sources is returned.
    """
    output = StringIO()
    for counter, filename in enumerate(files):
        print "Processing %s (file %d of %d)." % (filename, counter+1, len(files))
        if (
            isinstance(options.bmaj, float)
            and isinstance(options.bmin, float)
            and isinstance(options.bpa, float)
        ):
            ff = FitsFile(filename, beam=(options.bmaj, options.bmin, options.bpa), plane=0)
        else:
            ff = FitsFile(filename, plane=0)
        imagedata = sourcefinder_image_from_accessor(ff)
        if options.fdr:
            print "Using False Detection Rate algorithm with alpha = %f" % (options.alpha,)
            sr = imagedata.fd_extract(options.alpha)
        else:
            print "Thresholding with det = %f sigma, analysis = %f sigma" % (options.detection, options.analysis)
            sr = imagedata.extract(options.detection, options.analysis)
        if options.regions:
            regionfile = os.path.splitext(os.path.basename(filename))[0] + ".reg"
            regionfile = open(regionfile, 'w')
            regionfile.write(regions(sr))
            regionfile.close()
        if options.residuals or options.islands:
            gaussian_map, residual_map = generate_result_maps(imagedata.data, sr)
        if options.residuals:
            residualfile = os.path.splitext(os.path.basename(filename))[0] + ".residuals.fits"
            writefits(residualfile, residual_map, pyfits.getheader(filename))
        if options.islands:
            islandfile = os.path.splitext(os.path.basename(filename))[0] + ".islands.fits"
            writefits(islandfile, gaussian_map, pyfits.getheader(filename))
        if options.rmsmap:
            rmsfile = os.path.splitext(os.path.basename(filename))[0] + ".rms.fits"
            writefits(rmsfile, numpy.array(imagedata.rmsmap), pyfits.getheader(filename))
        if options.sigmap:
            sigfile = os.path.splitext(os.path.basename(filename))[0] + ".sig.fits"
            writefits(sigfile, numpy.array(imagedata.data_bgsubbed/imagedata.rmsmap), pyfits.getheader(filename))
        if options.skymodel:
            skymodelfile = os.path.splitext(os.path.basename(filename))[0] + ".skymodel"
            skymodelfile = open(skymodelfile, 'w')
            if ff.freqeff:
                skymodelfile.write(skymodel(sr, ff.freqeff))
            else:
                print "WARNING: Using default reference frequency for %s" % (skymodelfile.name,)
                skymodelfile.write(skymodel(sr))
            skymodelfile.close()
        if options.csv:
            csvfile = os.path.splitext(os.path.basename(filename))[0] + ".csv"
            csvfile = open(csvfile, 'w')
            csvfile.write(csv(sr))
            csvfile.close()
        print >>output, summary(filename, sr),
    return output.getvalue()


if __name__ == "__main__":
    options, files = handle_args()
    if files:
        set_configuration(options)
        print run_sourcefinder(files, options),
    else:
        print "No files to process specified."
