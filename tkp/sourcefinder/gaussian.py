# -*- coding: utf-8 -*-

"""

.. module:: gaussian

.. moduleauthor:: TKP, Hanno Spreeuw <software@transientskp.org>


:synposis: Definition of the elliptical Gaussian function.

"""

from numpy import exp, log, cos, sin

FIT_PARAMS = ('peak', 'xbar', 'ybar', 'semimajor', 'semiminor', 'theta')

def gaussian(height, center_x, center_y, semimajor, semiminor, theta):
    """Return a 2D Gaussian function with the given parameters.

    :argument height: (z-)value of the 2D Gaussian
    :type height: float

    :argument center_x: x center of the Gaussian
    :type center_x: float

    :argument center_y: y center of the Gaussian
    :type center_y: float

    :argument semimajor: major axis of the Gaussian
    :type semimajor: float

    :argument semiminor: minor axis of the Gaussian
    :type semiminor: float

    :argument theta: angle of the 2D Gaussian in radians, measured
        between the semi-major and y axes, in counterclockwise
        direction
    :type theta: float

    Theta is the angle between the semi-major & y axes measured in
    radians, measured counterclockwise.

    :returns: 2D Gaussian
    :rtype: function

    """

    return lambda x, y: height * exp(
        -log(2.0) * (((cos(theta) * (x - center_x) +
                            sin(theta) * (y - center_y)) /
                           semiminor)**2.0 +
                          ((cos(theta) * (y - center_y) -
                            sin(theta) * (x - center_x)) /
                           semimajor)**2.))
