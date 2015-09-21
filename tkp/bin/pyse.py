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
import argparse
import numpy
import astropy.io.fits as pyfits

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


def get_argparser():
    parser = argparse.ArgumentParser(
        description="Source extraction for radio-synthesis images")

    #Arguments relating to source extraction:
    extraction = parser.add_argument_group("Extraction")
    extraction.add_argument("--detection", default=10, type=float,
                        help="Detection threshold")
    extraction.add_argument("--analysis", default=3, type=float,
                        help="Analysis threshold")
    extraction.add_argument("--fdr", action="store_true",
                        help="Use False Detection Rate algorithm")
    extraction.add_argument("--alpha", default=1e-2, type=float, help="FDR Alpha")
    extraction.add_argument("--deblend-thresholds", default=0, type=int,
                        help="Number of deblending subthresholds; 0 to disable")
    extraction.add_argument("--grid", default=64, type=int,
                        help="Background grid segment size")
    extraction.add_argument("--margin", default=0, type=int,
                        help="Margin applied to each edge of image (in pixels)")
    extraction.add_argument("--radius", default=0, type=float,
                        help="Radius of usable portion of image (in pixels)")
    extraction.add_argument("--bmaj", type=float, help="Set beam: Major axis of beam (deg)")
    extraction.add_argument("--bmin", type=float, help="Set beam: Minor axis of beam (deg)")
    extraction.add_argument("--bpa", type=float, help="Set beam: Beam position angle (deg)")
    extraction.add_argument("--force-beam", action="store_true",
                        help="Force fit axis lengths to beam size")
    extraction.add_argument("--detection-image", type=str,
                        help="Find islands on different image")
    extraction.add_argument('--fixed-posns', help="List of position coordinates to "
        "force-fit (decimal degrees, JSON, e.g [[123.4,56.7],[359.9,89.9]]) "
        "(Will not perform blind extraction in this mode)"              ,
        default=None)
    extraction.add_argument('--fixed-posns-file',
        help="Path to file containing a list of positions to force-fit "
             "(Will not perform blind extraction in this mode)",
        default=None)
    extraction.add_argument('--ffbox', type=float, default=3.,
        help="Forced fitting positional box size as a multiple of beam width.")

    #Arguments relating to output:
    output = parser.add_argument_group("Output")
    output.add_argument("--skymodel", action="store_true",
                        help="Generate sky model")
    output.add_argument("--csv", action="store_true",
                        help="Generate csv text file for use in programs such as TopCat")
    output.add_argument("--regions", action="store_true",
                        help="Generate DS9 region file(s)")
    output.add_argument("--rmsmap", action="store_true",
                        help="Generate RMS map")
    output.add_argument("--sigmap", action="store_true",
                        help="Generate significance map")
    output.add_argument("--residuals", action="store_true",
                        help="Generate residual maps")
    output.add_argument("--islands", action="store_true",
                        help="Generate island maps")

    #Finally, positional arguments- the file list:
    parser.add_argument('files', nargs='+',
                        help="Image files for processing")
    return parser


def handle_args(args=None):
    """
    Parses command line options & arguments using OptionParser.
    Options & default values for the script are defined herein.
    """
    parser = get_argparser()
    options= parser.parse_args()

    # Overwrite 'fixed_coords' with a parsed list of coords
    # collated from both command line and file.
    options.fixed_coords = parse_monitoringlist_positions(
        options, str_name="fixed_posns", list_name="fixed_posns_file"
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

    return options, options.files

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
        "back_size_x": options.grid,
        "back_size_y": options.grid,
        "margin": options.margin,
        "radius": options.radius,
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
                options.ffbox * max(imagedata.beam[0:2])
            )

        else:
            if options.mode == "fdr":
                print "Using False Detection Rate algorithm with alpha = %f" % (options.alpha,)
                sr = imagedata.fd_extract(
                    alpha=options.alpha,
                    deblend_nthresh=options.deblend_thresholds,
                    force_beam=options.force_beam
                )
            else:
                if labelled_data is None:
                    print "Thresholding with det = %f sigma, analysis = %f sigma" % (options.detection, options.analysis)

                sr = imagedata.extract(
                    det=options.detection, anl=options.analysis,
                    labelled_data=labelled_data, labels=labels,
                    deblend_nthresh=options.deblend_thresholds,
                    force_beam=options.force_beam
                )

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
    print run_sourcefinder(files, options),
