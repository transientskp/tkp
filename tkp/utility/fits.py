import os
import math
import shutil

import casacore
import casacore.images
import casacore.tables
import astropy.io.fits as pyfits

import datetime


MJD0 = datetime.datetime(1858, 11, 17, 0, 0, 0)

def fix_reference_dec(imagename):
    """
    If the FITS file specified has a reference dec of 90 (or pi/2), make it
    infinitesimally less. This works around problems with ill-defined
    coordinate systems at the north celestial pole.
    """
    # TINY is an arbitrary constant which we regard as "far enough" away from
    # dec 90 (or pi/2). In theory, we ought to be able to us
    # sys.float_info.epsilon, but pyfits seems to round this when writing it
    # to a FITS file so that isn't quite generous enough.
    TINY = 1e-10
    with pyfits.open(imagename, mode='update') as ff:
        # The FITS standard (version 3.0, July 2008) tells us "For angular
        # measurements given as floating-point values [...] the units should
        # be degrees". We therefore use that as a default, but handle radians
        # too, just to be on the safe side.
        critical_value = 90.0 # degrees
        if "CUNIT2" in ff[0].header and ff[0].header["CUNIT2"] == "rad":
            critical_value = math.pi/2 # radians

        ref_dec = ff[0].header['CRVAL2']
        if (critical_value - abs(ref_dec)) < TINY:
            ff[0].header['CRVAL2'] = ref_dec * (1 - TINY)
            ff.flush()


def convert(casa_image, ms, fits_filename=None):
    """Convert a CASA image to FITS, taking care of header keywords

    :argument casa_image: CASA image
    :type casa_image: casacore.images.image
    :argument ms: CASA measurement set
    :type ms: casacore.tables.table

    :keyword fits_filename: FITS output filename
    :type fits_filename: str

    :returns: None

    """

    if fits_filename is None:
        fits_filename = os.path.splitext(casa_image)[0] + ".fits"

    # To do:
    # It would probably be more efficient (less IO)
    # to create a pyfits HDU object from the casa image data,
    # but I'm not sure how correct the coordinate conversion
    # would be.
    # Currently using the easy way
    image = casacore.images.image(casa_image)
    image.tofits(fits_filename)
    hdulist = pyfits.open(fits_filename, mode='update')
    header = hdulist[0].header
    # Obtain header info from original MS
    t0 = casacore.tables.table(ms, ack=False)
    header.update('OBS-ID', t0.getcol('OBSERVATION_ID')[0])

    t = casacore.tables.table(t0.getkeyword('SPECTRAL_WINDOW'), ack=False)
    header.update('SUBBAND', t.getcol('NAME')[0])
    header.update('REFFREQ', t.getcol('REF_FREQUENCY')[0])
    header.update('BANDWIDT', t.getcol('TOTAL_BANDWIDTH')[0])
    header.update('FREQUNIT', 'MHz')

    t = casacore.tables.table(t0.getkeyword('FIELD'), ack=False)
    phasedir = t.getcol('PHASE_DIR')
    phase_ra = phasedir[0][0][0] * 180 / math.pi
    if phase_ra < 0:
        phase_ra += 360
    header.update('phasera', phase_ra, 'degrees')
    header.update('phasedec', phasedir[0][0][1] * 180 / math.pi, 'degrees')
    header.update('field', t.getcol('NAME')[0])

    # When the MS we access is actually a slice through a current MS,
    # we can't rely on the timing information in the header to be correct
    # Instead, we obtain the actual timing information from the TIME
    # column in the actual data table.
    time_table = t0.query("", sortlist="TIME", limit=1, columns="TIME")
    start_time = MJD0 + datetime.timedelta(0, time_table.getcol('TIME')[0], 0)
    time_table = t0.query("", sortlist="-TIME", limit=1, columns="TIME")
    end_time = MJD0 + datetime.timedelta(0, time_table.getcol('TIME')[0], 0)
    mid_time  = start_time + (end_time - start_time) / 2
    header.update('date-obs', start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                  "Start time of observation")
    header.update('STARTUTC', start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                  "Start time of observation")
    header.update('END_UTC', end_time.strftime("%Y-%m-%dT%H:%M:%S"),
                  "End time of observation")
    header.update('MID_UTC', mid_time.strftime("%Y-%m-%dT%H:%M:%S"),
                  "Mid time of observation")

    t = casacore.tables.table(t0.getkeyword('OBSERVATION'), ack=False)
    header.update('OBSERVER', t.getcol('OBSERVER')[0])
    header.update('TELESCOP', t.getcol('TELESCOPE_NAME')[0])

    header.update('PIPENAME', 'TRAP')
    header.update('PIPE_VER', '0.1')

    hdulist.close()


def combine(fitsfiles, outputfile, method="average"):
    """Combine a set of FITS files, taking care of header keywords

    :argument fitsfiles: FITS filenames to combine
    :type fitsfiles: list
    :argument outputfile: output FITS filename
    :type outputfile: str

    :keyword method: average or sum the images
    :type method: str

    :returns: None

    """

    if method is None:
        return
    N = len(fitsfiles)
    if N == 1:
        shutil.copyfile(fitsfiles[0], outputfile)
        return
    hdulist0 = pyfits.open(fitsfiles[0])
    header0 = hdulist0[0].header
    data = hdulist0[0].data
    freqs = [header0['reffreq']]
    header0.update('orig0', os.path.basename(fitsfiles[0]),
                   'original fitsfile')
    for i, filename in enumerate(fitsfiles[1:]):
        with pyfits.open(filename) as hdulist:
            header = hdulist[0].header
            data += hdulist[0].data
        freqs.append(header['reffreq'])
        header0.update(
            'orig%d' % (i + 1), os.path.basename(filename),
            'original fitsfile')
    if method == "average":
        data /= float(N)

    minfreq, maxfreq = min(freqs), max(freqs)
    hdu = pyfits.PrimaryHDU(data)
    reffreq = (minfreq + maxfreq) / 2
    bandwidth = maxfreq - minfreq
    header0.update('reffreq', reffreq,
                  'reference frequency')
    header0.update('bandwidt', bandwidth,
                  'estimated bandwidth')
    header0.update('FREQ_MIN', minfreq,
                  'minimum frequency')
    header0.update('FREQ_MAX', maxfreq,
                  'maximum frequency')
    # frequencies are stored in WCS coords (dimension 4),
    # but since we've copied those from the first image,
    # they need to be updated
    header0.update('crval4', reffreq)
    header0.update('cdelt4', bandwidth)
    hdu.header = header0
    hdulist = pyfits.HDUList([hdu])
    hdulist.writeto(outputfile)
    hdulist.close()
    hdulist0.close()
