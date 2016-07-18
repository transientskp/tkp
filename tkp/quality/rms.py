import numpy
from tkp.utility import nice_format
from scipy.stats import norm
from tkp.db.quality import reject, reject_reasons
from tkp.db.model import Image
from sqlalchemy import not_


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


def reject_bad_rms_with_dataset_rms(session, dataset_id, est_sigma):
    """
    Reject images based on the RMS value of the full dataset.

    Images with rms_qc value outside of a rms range controlled with est_sigma
     wil be rejected:

       !(mu - sigma * est_sigma < rms_qc < mu + sigma * est_sigma)

    will be rejected.

    Args:
        session (sqlalchemy.Session): A SQLAlchemy session
        dataset_id (int): The ID of the dataset to use
        est_sigma (float): The sigma multiplication factor controlling upper
                           and lower rejection threshold
    """
    images = session.query(Image.rms_qc).filter(Image.dataset_id == dataset_id).all()
    mu, sigma = norm.fit(images)
    t_low = mu - sigma * est_sigma
    t_high = mu + sigma * est_sigma
    bad_images = session.query(Image).filter(not_(Image.rms_qc.between(t_low, t_high))).all()
    reason = reject_reasons['rms']
    for b in bad_images:
        comment = "RMS of {} is outside range of ({:.3f}, {:.3f}), est_sigma={}".format(b.rms_qc, t_low, t_high, est_sigma)
        reject(b.id, reason, comment, session)
    return bad_images
