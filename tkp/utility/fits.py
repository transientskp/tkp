import os, sys
import datetime
import math
from cStringIO import StringIO
import shutil
import pyrap
import pyrap.images
import pyrap.tables
import pyfits

MJD0 = datetime.datetime(1858, 11, 17, 0, 0, 0)


def convert(casa_image, ms, fits_filename=None):
    """Convert a CASA image to FITS, taking care of header keywords

    Args:
        casa_image (pyrap.images.image): CASA image
        ms (pyrap.tables.table): CASA measurement set

    Kwargs:
        fits_filename (str): FITS output filename

    Returns:
        None

    """

    if fits_filename is None:
        fits_filename = os.path.splitext(casa_image)[0] + ".fits"
                        
    # To do:
    # It would probably be more efficient (less IO)
    # to create a pyfits HDU object from the casa image data,
    # but I'm not sure how correct the coordinate conversion
    # would be.
    # Currently using the easy way    
    image = pyrap.images.image(casa_image)
    image.tofits(fits_filename)
    hdulist = pyfits.open(fits_filename, mode='update')
    header = hdulist[0].header
    # Obtain header info from original MS
    t0 = pyrap.tables.table(ms, ack=False)
    header.update('OBS-ID', t0.getcol('OBSERVATION_ID')[0])

    t  = pyrap.tables.table(t0.getkeyword('SPECTRAL_WINDOW'), ack=False)
    header.update('SUBBAND', t.getcol('NAME')[0])
    header.update('REFFREQ', t.getcol('REF_FREQUENCY')[0])
    header.update('BANDWIDT', t.getcol('TOTAL_BANDWIDTH')[0])
    header.update('FREQUNIT', 'MHz')
    
    t = pyrap.tables.table(t0.getkeyword('FIELD'), ack=False)
    phasedir = t.getcol('PHASE_DIR')
    phase_ra = phasedir[0][0][0]*180/math.pi
    if phase_ra < 0:
        phase_ra += 360
    header.update('phasera', phase_ra, 'degrees')
    header.update('phasedec', phasedir[0][0][1]*180/math.pi, 'degrees')
    header.update('field', t.getcol('NAME')[0])

    # When the MS we access is actually a slice through a current MS,
    # we can't rely on the timing information in the header to be correct
    # Instead, we obtain the actual timing information from the TIME
    # column in the actual data table.
    time_table = t0.query("", sortlist="TIME", limit=1, columns="TIME")
    start_time = MJD0 + datetime.timedelta(0, time_table.getcol('TIME')[0], 0)
    time_table = t0.query("", sortlist="-TIME", limit=1, columns="TIME")
    end_time = MJD0 + datetime.timedelta(0, time_table.getcol('TIME')[0], 0)
    dt = end_time - start_time
    mid_time = (start_time +
                datetime.timedelta(dt.days, dt.seconds, dt.microseconds))
    header.update('date-obs', start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                  "Start time of observation")
    header.update('STARTUTC', start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                  "Start time of observation")
    header.update('END_UTC', end_time.strftime("%Y-%m-%dT%H:%M:%S"),
                  "End time of observation")
    header.update('MID_UTC', mid_time.strftime("%Y-%m-%dT%H:%M:%S"),
                  "Mid time of observation")

    t = pyrap.tables.table(t0.getkeyword('OBSERVATION'), ack=False)
    header.update('OBSERVER', t.getcol('OBSERVER')[0])
    release_date = t.getcol('RELEASE_DATE')
    header.update('TELESCOP', t.getcol('TELESCOPE_NAME')[0])

    header.update('PIPENAME', 'TRAP')
    header.update('PIPE_VER', '0.1')
    
    hdulist.close()


def combine(fitsfiles, outputfile, method="average"):
    """Combine a set of FITS files, taking care of header keywords

    Args:
        fitsfiles (list): list of FITS filenames to combine
        outputfile (str): output FITS filename

    Kwargs:
        method (str): average or sum the images

    Returns:
        None

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
        hdulist = pyfits.open(filename)
        header = hdulist[0].header
        data += hdulist[0].data
        freqs.append(header['reffreq'])
        header0.update(
            'orig%d' % (i+1), os.path.basename(filename),
            'original fitsfile')
    if method == "average":
        data /= float(N)

    minfreq, maxfreq = min(freqs), max(freqs)
    hdu = pyfits.PrimaryHDU(data)
    reffreq = (minfreq + maxfreq)/2
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
