#!/usr/bin/env python
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
import numbers
import os.path
from cStringIO import StringIO
from optparse import OptionParser
import numpy
import pyfits

import logging

from tkp.accessors import open as open_accessor
from tkp.accessors import sourcefinder_image_from_accessor
from tkp.accessors import writefits as tkp_writefits
from tkp.sourcefinder.utils import generate_result_maps
from tkp.management import parse_monitoringlist_positions

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
        # NB, here we convert from internal 0-origin indexing to DS9 1-origin indexing
        print >>output, "ellipse(%f, %f, %f, %f, %f)" % (
            source.x.value + 1.0,
            source.y.value + 1.0,
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
    print >> output, "ra, ra_err, dec, dec_err, smaj, smaj_err, smin, smin_err, pa, pa_err, int_flux, int_flux_err, pk_flux, pk_flux_err"
    for source in sourcelist:
        print >> output, "%f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f, %f" % (
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
        print >>output, "Error radius (arcsec): %s" % (str(source.error_radius))
        print >>output, "Semi-major axis (arcsec): %s" % (str(source.smaj_asec))
        print >>output, "Semi-minor axis (arcsec): %s" % (str(source.smin_asec))
        print >>output, "Position angle: %s" % (str(source.theta_celes))
        print >>output, "Flux: %s" % (str(source.flux))
        print >>output, "Peak: %s\n" % (str(source.peak))
    return output.getvalue()

def handle_args(args=None):
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
    parser.add_option("--bmaj", type="float", help="Major axis of beam (deg)")
    parser.add_option("--bmin", type="float", help="Minor axis of beam (deg)")
    parser.add_option("--bpa", type="float", help="Beam position angle (deg)")
    parser.add_option("--grid", default=64, type="int", help="Background grid segment size")
    parser.add_option("--margin", default=0, type="int", help="Margin applied to each edge of image (in pixels)")
    parser.add_option("--radius", default=0, type="float", help="Radius of usable portion of image (in pixels)")
    parser.add_option("--skymodel", action="store_true", help="Generate sky model")
    parser.add_option("--nproc",default=1, type="int", help="Number of processes to use")
    parser.add_option("--csv", action="store_true", help="Generate csv text file for use in programs such as TopCat")
    parser.add_option("--rmsmap", action="store_true", help="Generate RMS map")
    parser.add_option("--sigmap", action="store_true", help="Generate significance map")
    parser.add_option("--force-beam", action="store_true", help="Force fit axis lengths to beam size")
    parser.add_option("--detection-image", type="string", help="Find islands on different image")
    m_help = "Specify a list of RA,Dec co-ordinate positions to force-fit " \
        '(decimal degrees, JSON format e.g. "[[144.2,33.3],[146.1,34.1]]" )'
    parser.add_option('--fixed', help=m_help, default=None)
    parser.add_option('--fixed-list',
        help="Specify a file containing a list of positions to force-fit", default=None
    )
    box_help = "Specify forced fitting positional freedom / error-box size, " \
        "as a multiple of beam width."
    parser.add_option('--ffbox-in-beampix', type='float', default=3., help=box_help)
    options, files = parser.parse_args(args=args)

    # Overwrite 'fixed_coords' with a parsed list of coords
    # collated from both command line and file.
    options.fixed_coords = parse_monitoringlist_positions(
        options, str_name="fixed", list_name="fixed_list"
    )
    # Quick & dirty check that the position list looks plausible
    if options.fixed_coords:
        mlist = numpy.array(options.fixed_coords)
        if not (len(mlist.shape) == 2 and mlist.shape[1] == 2):
            parser.error("Positions for forced-fitting must be [RA,dec] pairs")

    # We have four potential modes, of which we choose only one to run:
    #
    # 1. Blind sourcefinding
    #  1.1 Thresholding, no detection image (no extra cmd line options)
    #  1.2 Thresholding, detection image (--detection-image)
    #  1.3 FDR (--fdr)
    #
    # 2. Fit to fixed points (--fixed-coords and/or --fixed-list)

    if options.fixed_coords:
        if options.fdr:
            parser.error("--fdr not supported with fixed positions")
        elif options.detection_image:
            parser.error("--detection-image not supported with fixed positions")
        options.mode = "fixed" # mode 2 above
    elif options.fdr:
        if options.detection_image:
            parser.error("--detection-image not supported with --fdr")
        options.mode = "fdr" # mode 1.3 above
    elif options.detection_image:
        options.mode = "detimage" # mode 1.2 above
    else:
        options.mode = "threshold" # mode 1.1 above

    return options, files

def writefits(filename, data, header={}):
    try:
        os.unlink(filename)
    except OSError:
        # Thrown if file didn't exist
        pass
    tkp_writefits(data, filename, header)

def get_detection_labels(filename, det, anl, beam, configuration, plane=0):
    print "Detecting islands in %s" % (filename,)
    print "Thresholding with det = %f sigma, analysis = %f sigma" % (det, anl)
    ff = open_accessor(filename, beam=beam, plane=plane)
    imagedata = sourcefinder_image_from_accessor(ff, **configuration)
    labels, labelled_data = imagedata.label_islands(
        det * imagedata.rmsmap, anl * imagedata.rmsmap
    )
    return labels, labelled_data

def get_sourcefinder_configuration(options):
    configuration = {
        "back_sizex": options.grid,
        "back_sizey": options.grid,
        "margin": options.margin,
        "radius": options.radius,
        "deblend": bool(options.deblend),
        "deblend_nthresh": options.deblend_thresholds,
        "force_beam": options.force_beam,
	"nproc" : options.nproc
    }
    if options.residuals or options.islands:
        configuration['residuals'] = True
    return configuration

def get_beam(bmaj, bmin, bpa):

    if (
        isinstance(bmaj, numbers.Real)
        and isinstance(bmin, numbers.Real)
        and isinstance(bpa, numbers.Real)
    ):
        return (float(bmaj), float(bmin), float(bpa))
    if bmaj or bmin or bpa:
        print "WARNING: partial beam specification ignored"
    return None

def bailout(reason):
    # Exit with error
    print "ERROR: %s" % (reason)
    sys.exit(1)

def run_sourcefinder(files, options):
    """
    Iterate over the list of files, running a sourcefinding step on each in
    turn. If specified, a DS9-compatible region file and/or a FITS file
    showing the residuals after Gaussian fitting are dumped for each file.
    A string containing a human readable list of sources is returned.
    """
    output = StringIO()

    beam = get_beam(options.bmaj, options.bmin, options.bpa)
    configuration = get_sourcefinder_configuration(options)

    if options.mode == "detimage":
        labels, labelled_data = get_detection_labels(
            options.detection_image, options.detection, options.analysis, beam, configuration
        )
    else:
        labels, labelled_data = [], None

    for counter, filename in enumerate(files):
        print "Processing %s (file %d of %d)." % (filename, counter+1, len(files))
        imagename = os.path.splitext(os.path.basename(filename))[0]
        ff = open_accessor(filename, beam=beam, plane=0)
        imagedata = sourcefinder_image_from_accessor(ff, **configuration)

        if options.mode == "fixed":
            sr = imagedata.fit_fixed_positions(options.fixed_coords,
                options.ffbox_in_beampix * max(imagedata.beam[0:2])
            )

        else:
            if options.mode == "fdr":
                print "Using False Detection Rate algorithm with alpha = %f" % (options.alpha,)
                sr = imagedata.fd_extract(options.alpha)
            else:
                if labelled_data is None:
                    print "Thresholding with det = %f sigma, analysis = %f sigma" % (options.detection, options.analysis)
                sr = imagedata.extract(options.detection, options.analysis, labelled_data=labelled_data, labels=labels)

        if options.regions:
            regionfile = imagename + ".reg"
            regionfile = open(regionfile, 'w')
            regionfile.write(regions(sr))
            regionfile.close()
        if options.residuals or options.islands:
            gaussian_map, residual_map = generate_result_maps(imagedata.data, sr)
        if options.residuals:
            residualfile = imagename + ".residuals.fits"
            writefits(residualfile, residual_map, pyfits.getheader(filename))
        if options.islands:
            islandfile = imagename + ".islands.fits"
            writefits(islandfile, gaussian_map, pyfits.getheader(filename))
        if options.rmsmap:
            rmsfile = imagename + ".rms.fits"
            writefits(rmsfile, numpy.array(imagedata.rmsmap), pyfits.getheader(filename))
        if options.sigmap:
            sigfile = imagename + ".sig.fits"
            writefits(sigfile, numpy.array(imagedata.data_bgsubbed / imagedata.rmsmap), pyfits.getheader(filename))
        if options.skymodel:
            with open(imagename + ".skymodel", 'w') as skymodelfile:
                if ff.freq_eff:
                    skymodelfile.write(skymodel(sr, ff.freq_eff))
                else:
                    print "WARNING: Using default reference frequency for %s" % (skymodelfile.name,)
                    skymodelfile.write(skymodel(sr))
        if options.csv:
            with open(imagename + ".csv", 'w') as csvfile:
                csvfile.write(csv(sr))
        print >>output, summary(filename, sr),
    return output.getvalue()


if __name__ == "__main__":
    logging.basicConfig()
    options, files = handle_args()
    if files:
        print run_sourcefinder(files, options),
    else:
        print "No files to process specified."
