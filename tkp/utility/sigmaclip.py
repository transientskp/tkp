"""
Generic kappa-sigma clipping routine.

Note: this does *not* replace the specialized sigma_clip function in
utilities.py
"""

from __future__ import division
import numpy

def clip(data, mean, sigma, siglow, sighigh, indices=None):
    """Perform kappa-sigma clipping of data around mean

    Args:

        data (numpy.ndarray): N-dimensional array of values

        mean (float): value around which to clip (does not have to be the mean)

        sigma (float): sigma-value for clipping

        siglow (float): lower kappa clipping values

        sighigh (float): higher kappa clipping values

    Kwargs:

        indices (numpy.ndarray): data selection by indices

    Returns:

        (numpy.ndarray) indices of non-clipped data

    """

    if indices is not None:
        ilow = numpy.logical_and(data >= mean - sigma * siglow, indices)
        ihigh = numpy.logical_and(data <= mean + sigma * sighigh, indices)
    else:
        ilow = data >= mean - sigma * siglow
        ihigh = data <= mean + sigma * sighigh
    indices = numpy.logical_and(ilow, ihigh)
    return indices


def calcmean(data, errors=None):
    """Calculate the mean and the standard deviation of the mean"""

    N = len(data)
    if errors is None:
        mean = data.sum() / N
        sigma = numpy.sqrt(((data**2).sum() - N * mean**2) / (N - 1) / N)
    else:
        w = 1. / errors**2
        mean = (w * data).sum() / w.sum()
        sigma = numpy.sqrt(1. / w.sum())
    return mean, sigma


def calcsigma(data, errors=None, mean=None, axis=None, errors_as_weight=False):
    """Calculate the sample standard deviation

    Args:

        data (numpy.ndarray): Data to be averaged. No conversion from
            eg a list to a numpy.array is done.

    Kwargs:

        errors (numpy.ndarray, None): Eerrors for the data. Errors
            needs to be the same shape as data (this is different than
            for numpy.average).  If you want to use weights instead of
            errors as input, set errors_as_weight=True.  If not given,
            all errors (and thus weights) are assumed to be equal to
            1.

        mean (float): Provide mean if you don't want the mean to be
            calculated for you. Pay careful attention to the shape if
            you provide 'axis'.

        axis (int): Specify axis along which the mean and sigma are
           calculated.  If not provided, calculations are done over
           the whole array

        errors_as_weight (bool): Set to True if errors are weights.

    Returns:

        (2-tuple of floats) mean and sigma
    """

    N = data.shape[axis] if axis else len(data)
    if errors is None:
        w = None
    elif errors_as_weight:
        w = errors
    else:
        w = 1.0 / (errors * errors)
    if mean is None:
        # numpy.average does have a weight option, but may
        # not be available in all numpy versions
        mean = ((w * data).sum(axis) / (w.sum(axis))
                if w is not None else data.sum(axis) / N)
    if w is not None:
        V1 = w.sum(axis)
        V2 = (w * w).sum(axis)
        # weighted sample variance
        if axis:
            shape = list(mean.shape)
            shape.insert(axis, 1)
            mmean = numpy.array(mean, copy=0, ndmin=data.ndim).reshape(shape)
        else:
            mmean = mean
        sigma = numpy.sqrt(((data - mmean) * (data - mmean) * w).sum(axis) *
                            (V1 / (V1 * V1 - V2)))
    else:
        # unweighted sample variance
        sigma = numpy.sqrt(((data * data).sum(axis) - N * mean * mean) /
                           (N - 1))
    return mean, sigma


def sigmaclip(data, errors=None, niter=0, siglow=3., sighigh=3.,
              use_median=False):
    """Remove outliers from data which lie more than siglow/sighigh
    sample standard deviations from mean.

    Args:

        data (numpy.ndarray): Numpy array containing data values.

    Kwargs:

        errors (numpy.ndarray, None): Errors associated with the data
            values. If None, unweighted mean and standard deviation
            are used in calculations.

        niter (int): Number of iterations to calculate mean & standard
            deviation, and reject outliers, If niter is negative,
            iterations will continue until no more clipping occurs or
            until abs('niter') is reached, whichever is reached first.

        siglow (float): Kappa multiplier for standard deviation. Std *
            siglow defines the value below which data are rejected.

        sighigh (float): Kappa multiplier for standard deviation. Std *
            sighigh defines the value above which data are rejected.

        use_median (bool): Use median of data instead of mean.

    Returns:

        tuple: (2-tuple) Boolean numpy array of indices indicating which
            elements are clipped (False), with the same shape as the
            input; number of iterations

    """

    # indices keeps track which data should be discarded
    indices = numpy.ones(len(data.ravel()), dtype=numpy.bool).reshape(
        data.shape)
    nniter = -niter if niter < 0 else niter
    i = 0
    for i in range(nniter):
        newdata = data[indices]
        newerrors = errors[indices] if errors is not None else None
        N = len(newdata)
        if N < 2:
            return indices, i
        if use_median:
            mean = numpy.median(newdata)
        else:
            mean = None
        mean, sigma = calcsigma(newdata, newerrors, mean)
        newindices = clip(data, mean, sigma, siglow, sighigh)
        if niter < 0:
            # break when no changes
            if (newindices == indices).all():
                break
        indices = newindices
    return indices, i + 1
