"""
placeholder for all quality checking related code.

The quality checks are described in the "LOFAR Transients Key Science Project Quality Control Document V1.1"

"""


def rms_too_high(rms, noise, factor=1):
    """ Is the RMS value of an image too high?
    Args:
        rms: RMS value of an image, can be computed with tkp.quality.statistics.rms
        noise: Theoretical noise level of instrument, can be calculated with tkp.lofar.noise.noise_level
        factor: The allowed factor
    """
    return rms > noise * factor

