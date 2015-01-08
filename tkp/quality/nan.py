import numpy as np


def contains_nan(array):
    """
    Checks if a numpy array contains a NaN value.

    A NaN values may indicate a calibration error. The source finder doesn't
    know how to interpret a NaN value so we reject such an image.

    args:
        array: a Numpy array
        
    Returns:
        Error string if array contains NaN, False otherwise
    """
    # summing an array containing NaN will result in NaN
    if np.isnan(np.sum(array)):
        return "Image data contains NaN value"
    else:
        return False
