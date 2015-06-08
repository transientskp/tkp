"""
Definition of a two dimensional elliptical Gaussian.
"""

from numpy import exp, log, cos, sin

def gaussian(height, center_x, center_y, semimajor, semiminor, theta):
    """Return a 2D Gaussian function with the given parameters.

    Args:

        height (float): (z-)value of the 2D Gaussian

        center_x (float): x center of the Gaussian

        center_y (float): y center of the Gaussian

        semimajor (float): major axis of the Gaussian

        semiminor (float): minor axis of the Gaussian

        theta (float): angle of the 2D Gaussian in radians, measured
            between the semi-major and y axes, in counterclockwise
            direction.

    Returns:
        lambda: 2D Gaussian (function of pixel coords ``(x,y)``)
    """

    return lambda x, y: height * exp(
        -log(2.0) * (((cos(theta) * (x - center_x) +
                            sin(theta) * (y - center_y)) /
                           semiminor)**2.0 +
                          ((cos(theta) * (y - center_y) -
                            sin(theta) * (x - center_x)) /
                           semimajor)**2.))
