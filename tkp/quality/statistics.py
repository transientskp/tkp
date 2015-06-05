"""
functions for calculating statistical properties of LOFAR images
"""
import numpy


def rms(data):
    """Returns the RMS of the data about the median.
    Args:
        data: a numpy array
    """
    data -= numpy.median(data)
    return numpy.sqrt(numpy.power(data, 2).sum()/len(data))


def clip(data, sigma=3):
    """Remove all values above a threshold from the array.
    Uses iterative clipping at sigma value until nothing more is getting clipped.
    Args:
        data: a numpy array
    """
    raveled = data.ravel()
    median = numpy.median(raveled)
    std = numpy.std(raveled)
    newdata = raveled[numpy.abs(raveled-median) <= sigma*std]
    if len(newdata) and len(newdata) != len(raveled):
        return clip(newdata, sigma)
    else:
        return newdata


def subregion(data, f=4):
    """Returns the inner region of a image, according to f.

    Resulting area is 4/(f*f) of the original.
    Args:
        data: a numpy array
    """
    x, y = data.shape
    return data[(x/2 - x/f):(x/2 + x/f), (y/2 - y/f):(y/2 + y/f)]


def rms_with_clipped_subregion(data, rms_est_sigma=3, rms_est_fraction=4):
    """
    RMS for quality-control.

    Root mean square value calculated from central region of an image.
    We sigma-clip the input-data in an attempt to exclude source-pixels
    and keep only background-pixels.

    Args:
        data: A numpy array
        rms_est_sigma: sigma value used for clipping
        rms_est_fraction: determines size of subsection, result will be
            1/fth of the image size where f=rms_est_fraction
    returns the rms value of a iterative sigma clipped subsection of an image
    """
    return rms(clip(subregion(data, rms_est_fraction), rms_est_sigma))
