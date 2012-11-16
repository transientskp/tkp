import re


def parse_fits(fitsfile):
    """
    Extract relevant info from headers in FITS file.
    This should go into the DataAccessor code some day
    """
    history = fitsfile.header['HISTORY*']
    xy_line = [i for i in history.values() if 'cellx' in i][0]
    extracted = re.search(r"cellx='(?P<x>\d+).*celly='(?P<y>\d+)", xy_line).groupdict()
    data = {}
    data['cellsize'] = int(extracted['x'])
    data['bmaj'] = fitsfile.header['BMAJ']
    data['bmin'] = fitsfile.header['BMIN']
    data['nx'] = fitsfile.header['NAXIS1']
    data['ny'] = fitsfile.header['NAXIS2']
    return data


def undersampled(semibmaj, semibmin):
    """
    We want more than 2 pixels across the beam major and minor axes.
    Semibmaj and semibmin describe the beam size in pixels
    """
    return semibmaj * 2 <= 1 or semibmin * 2 <= 1


def oversampled(semibmaj, semibmin, x=30):
    """
    It has been identified that having too many pixels across the restoring
    beam can lead to bad images, however further testing is required to
    determine the exact number.
    Returns:
        True if the beam is oversampled
    """
    return semibmaj > x or semibmin > x


def highly_elliptical(semibmaj, semibmin, x=2.0):
    """
    If the beam is highly elliptical it can cause source association
    problems within TraP. Again further testing is required to determine
    exactly where the cut needs to be.
    returns:
        True if the beam is highly elliptical
    """
    return semibmaj / semibmin > x


def not_full_fieldofview(nx, ny, cellsize, fov):
    """
    This has been raised as an interesting test, as if the full field of
    view (FOV) has not been imaged we may want to image the full dataset.
    The imaged FOV information can be estimated using the number of pixels
    and the size of the pixels. (nx and ny are the number of pixels in
    the x and y directions and are in the image header).
    :Returns:
        True if the full FOV is imaged
    """
    return nx * ny * (cellsize/3600) * (cellsize/3600) < fov


