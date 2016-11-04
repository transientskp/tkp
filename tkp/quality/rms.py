import numpy
from tkp.utility import nice_format
from scipy.stats import norm
from sqlalchemy.sql.expression import desc
from tkp.db.model import Image
from tkp.db.quality import reject_reasons

def rms_invalid(rms, noise, low_bound=1, high_bound=50):
    """
    Is the RMS value of an image outside the plausible range?

    :param rms: RMS value of an image, can be computed with
                tkp.quality.statistics.rms
    :param noise: Theoretical noise level of instrument, can be calculated with
                  tkp.lofar.noise.noise_level
    :param low_bound: multiplied with noise to define lower threshold
    :param high_bound: multiplied with noise to define upper threshold
    :returns: True/False
    """
    if (rms < noise * low_bound) or (rms > noise * high_bound):
        ratio = rms / noise
        return "rms value (%s) is %s times theoretical noise (%s)" % \
                    (nice_format(rms), nice_format(ratio), nice_format(noise))
    else:
        return False


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


def reject_historical_rms(image_id, session, history=100, est_sigma=4, rms_max=100., rms_min=0.0):
    """
    Check if the RMS value of an image lies within a range defined
    by a gaussian fit on the histogram calculated from the last x RMS
    values in this subband. Upper and lower bound are then controlled
    by est_sigma multiplied with the sigma of the gaussian.

    args:
        image_id (int): database ID of the image we want to check
        session (sqlalchemy.orm.session.Session): the database session
        history (int): the number of timestamps we want to use for histogram
        est_sigma (float): sigma multiplication factor
        rms_max (float): global maximum rms for image quality check
        rms_min (float): global minimum rms for image quality check
    returns:
        bool: None if not rejected, (rejectreason, comment) if rejected
    """
    image = session.query(Image).filter(Image.id == image_id).one()
    rmss = session.query(Image.rms_qc).filter(
        (Image.band == image.band)).order_by(desc(Image.taustart_ts)).limit(
        history).all()
    if len(rmss) < history:
        return False
    mu, sigma = norm.fit(rmss)
    t_low = mu - sigma * est_sigma
    t_high = mu + sigma * est_sigma

    if not rms_min < image.rms_qc < rms_max:
        return reject_reasons['rms'],\
               "RMS value not within {} and {}".format(0.0, rms_max)

    if not t_low < image.rms_qc < t_high or not 0.0 < image.rms_qc < rms_max:
        return reject_reasons['rms'],\
               "RMS value not within {} and {}".format(t_low, t_high)

