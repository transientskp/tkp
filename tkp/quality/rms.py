from tkp.utility import nice_format


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
