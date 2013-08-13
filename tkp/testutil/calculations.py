"""Python functions for sanity checking calculations done in SQL"""
from math import cos, radians, sqrt
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
     
    """
    dra_norm = (pos1.ra - pos2.ra) ** 2 / (pos1.ra_err ** 2 + pos2.ra_err ** 2)
    ddec_norm = (pos1.dec - pos2.dec) ** 2 / (pos1.dec_err ** 2 + pos2.dec_err ** 2)
    return sqrt(dra_norm + ddec_norm)

def deruiter_current(pos1, pos2):
    """Unfortunately wrong. See notes above."""
    delta_ra = pos1.ra * cos(radians(pos1.dec)) - pos2.ra * cos(radians(pos2.dec))
    delta_dec = pos1.dec - pos2.dec
    
    # Nominator is cos(dec) normalised, but denom isn't
    dra_norm = (delta_ra ** 2 /
                (pos1.ra_err ** 2 + pos2.ra_err ** 2))

    # This is fine
    ddec_norm = (delta_dec ** 2 /
                  (pos1.ra_err ** 2 + pos2.ra_err ** 2))
    # NB database version applies a correction factor of 3600 to the final
    # result - this is because the errors are in arcseconds there.
    return sqrt(dra_norm + ddec_norm)

