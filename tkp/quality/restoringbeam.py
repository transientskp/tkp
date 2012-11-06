import re


def parse_fits(fitsfile):
    history = fitsfile.header['HISTORY*']
    xy_line = [i for i in history.values() if 'cellx' in i][0]
    extracted = re.search(r"cellx='(?P<x>\d+).*celly='(?P<y>\d+)", xy_line).groupdict()
    cellsize = int(extracted['x'])
    bmaj = fitsfile.header['BMAJ']
    bmin = fitsfile.header['BMIN']
    return (bmaj, bmin, cellsize)


def undersampled(bmaj,bmin, cellsize):
    """
    We want more than 2 pixels across the beam major and minor axes. The
    beam axes are given in the image header in degrees and the pixel
    cellsize is also in the image header in arcsec.
    Returns:
        True if the beam is undersampled
    """
    return bmaj/(cellsize/3600.0) > 2 and bmin/(cellsize/3600.0) > 2


def oversampled(bmaj,bmin, cellsize, x=30):
    """
    It has been identified that having too many pixels across the restoring
    beam can lead to bad images, however further testing is required to
    determine the exact number.
    Returns:
        True if the beam is oversampled
    """
    return bmaj/(cellsize/3600.0) < x and bmin/(cellsize/3600.0) < x


def highly_elliptical(bmaj, bmin, x=2.0):
    """
    If the beam is highly elliptical it can cause source association
    problems within TraP. Again further testing is required to determine
    exactly where the cut needs to be.
    returns:
        True if the beam is highly elliptical
    """
    return bmaj/bmin < x


def full_fieldofview(nx, ny, cellsize, fov):
    """
    This has been raised as an interesting test, as if the full field of
    view (FOV) has not been imaged we may want to image the full dataset.
    The imaged FOV information can be estimated using the number of pixels
    and the size of the pixels. (nx and ny are the number of pixels in
    the x and y directions and are in the image header).
    :Returns:
        True if the full FOV is imaged
    """
    return nx*ny*(cellsize/3600)*(cellsize/3600) > fov


