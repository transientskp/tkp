"""
functions for calculating statistical properties of LOFAR images
"""
import numpy
import re
import math

def rms(data):
    """
    returns the clipped RMS of an image
    """
    clipped_data = clip(data.ravel())
    clipped_data -= numpy.median(clipped_data)
    return numpy.sqrt(numpy.power(clipped_data, 2).sum()/len(clipped_data))

def clip(data, sigma=3):
    """
    remove all values above a threshold from the array
    uses iterative clipping at sigma value until nothing more is getting clipped.
    """
    median = numpy.median(data)
    std = numpy.std(data)
    newdata = data[numpy.abs(data-median) <= sigma*std]
    if len(newdata) and len(newdata) != len(data):
        return clip(newdata, sigma)
    else:
        return newdata

def clip_mask(data, sigma=3):
    """
    returns a mask for values above threshold defined by sigma from median
    uses iterative clipping at sigma value until nothing more is getting clipped.
    """
    mask = numpy.zeros(data.shape, bool)
    new_mask = numpy.zeros(data.shape, bool)
    masked = data
    while True:
        median = numpy.median(masked)
        std = numpy.std(masked)
        new_mask[numpy.abs(data - median) > sigma * std] = True
        diff = new_mask & ~mask
        mask = mask | new_mask
        if not diff.any():
            return mask
        masked = data[~mask]
        new_mask[:,:] = False

def beam_correction(FitsImage):
    """ Calculates a beam correction from the beam properties

    TODO: this should probably be moved into the TKP Fits accessor

    Args:
        bmaj, bmin: beam properties
    """
    # extract pixel size from HISTORY junk in fits header.
    history = FitsImage.header['HISTORY*']
    xy_line = [i for i in history.values() if 'cellx' in i][0]
    extracted = re.search(r"cellx='(?P<x>\d+).*celly='(?P<y>\d+)", xy_line).groupdict()
    pixelsize = int(extracted['x']) # X and Y should be the same
    bmaj = FitsImage.header['BMAJ'] * 3600 # convert from degrees to arcsec
    bmin = FitsImage.header['BMIN'] * 3600

    bmaj_scaled = bmaj / pixelsize
    bmin_scaled = bmin / pixelsize
    area = math.pi * bmaj_scaled * bmin_scaled
    return area