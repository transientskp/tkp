"""
placeholder for all quality checking related code.

The quality checks are described in the "LOFAR Transients Key Science Project Quality Control Document V1.1"

"""

def rms_valid(rms, noise, low_factor=1, high_factor=50):
    """ Is the RMS value of an image too high?
    Args:
        rms: RMS value of an image, can be computed with tkp.quality.statistics.rms
        noise: Theoretical noise level of instrument, can be calculated with tkp.lofar.noise.noise_level
        low_factor: multiplied with noise to define lower threshold
        high_factor: multiplied with noise to define upper threshold
    """
    return (rms > noise * low_factor) and (rms < noise * high_factor)

