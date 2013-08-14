"""Python functions for sanity checking calculations done in SQL"""
from math import cos, radians, sqrt

def cross_meridian_predicate(ra1_in, ra2_in):
    """
    Returns True if the positions lie across the meridian.
    
    Useful for checking if the functions should be shifted 180 degrees
    before differencing, averaging, etc, in order to avoid meridian issues.
    
    NB. Makes no statement about whether or not you need to take modulo
    of the data! So e.g. 0,360 -> False, but clearly the average position
    should be 0 degrees, not 180! 
    """
    ra1, ra2 = ra1_in % 360, ra2_in % 360
    naive_sep = abs(ra1 - ra2)
    if naive_sep <= 180:
        return False
    shifted = abs((ra1 + 180.) % 360. - (ra2 + 180.) % 360.)
    if shifted <= naive_sep:
        return True
    raise AssertionError("Logic error in cross_meridian_predicate: "+
                         "values {0},{1}".format(ra1, ra2))


def deruiter(pos1, pos2):
    """pos1,2 should be of type ``PositionTuple``.
    
    For a definition, see Bart's thesis (Scheers2011), eq. 3.1, 3.2.
    
    
    Note1: One way to think of the DR calculation is as an error-normalized 
    version of the basic Pythagoras equation (using a flat approximation 
    to a localised section of the unit sphere). 
    So, when calculating delta_ra, we are actually just calculating the 
    distance along a line of constant latitude. Hence we only apply the 
    cos(Dec) correction from one position (dec1 or dec2). For sufficiently 
    close positions, the difference in value of cos(Dec1) vs. cos(Dec2) 
    is provably negligible (cross product with delta_ra to get vanishingly 
    small terms). 
    **However**, if we employ  **both** values 
    (applying a different correction to each RA value),
    then we get cross-product terms which can be significant, leading to 
    calculation errors.
    
    TO DO: Reproduce calculations on this, document in LaTeX format.
    
    Note2: On the unit sphere, naively, we must apply the (same) cos(Dec) 
    correction to all RA values (including errors) to convert them back to 
    local distances. But of course, that cancels out! Thereby simplifying our 
    calculations so that they resemble the simple Euclidean case.
    
    Note3: Since we want this function to be 'always correct' for testing 
    purposes (without regard to performance etc), we always take the value 
    of RA modulo 360, to ensure that wrappings are dealt with correctly. 
    Of course, this may be dealt with differently in production code.  
     
    """

    # Are we comparing across the meridian?
    if cross_meridian_predicate(pos1.ra, pos2.ra):
        delta_ra = (pos1.ra + 180.) % 360. - (pos2.ra + 180.) % 360.
    else:
        delta_ra = pos1.ra % 360.0 - pos2.ra % 360.0
    dra_norm = delta_ra ** 2 / (pos1.ra_err ** 2 + pos2.ra_err ** 2)
    ddec_norm = (pos1.dec - pos2.dec) ** 2 / (pos1.dec_err ** 2 + pos2.dec_err ** 2)
    return sqrt(dra_norm + ddec_norm)

