import math

def deconv(fmaj, fmin, fpa, cmaj, cmin, cpa):
    precision = 1e-12
    HALF_RAD = 90/math.pi
    #lfpa = (fpa + 900.0) % 180
    #lcpa = (cpa + 900.0) % 180
    lfpa = fpa
    lcpa = cpa
    cmaj2 = cmaj * cmaj
    cmin2 = cmin * cmin
    fmaj2 = fmaj * fmaj
    fmin2 = fmin * fmin
    theta = (lfpa - lcpa) / HALF_RAD
    cos_theta = math.cos(theta)
    sin_theta = math.sin(theta)
    
    rhoc = (fmaj2 - fmin2) * cos_theta - (cmaj2 - cmin2)
    if abs(rhoc) < precision:
        sigic2 = 0.0
        rhoa = 0.0
    else:
        sigic2 = math.atan((fmaj2 - fmin2) * sin_theta / rhoc)
        rhoa = (((cmaj2 - cmin2) - (fmaj2 - fmin2) * cos_theta) /
                (2.0 * math.cos(sigic2)))

    rpa = sigic2 * HALF_RAD + lcpa
    det = ((fmaj2 + fmin2) - (cmaj2 + cmin2)) / 2.0
    rmaj = det - rhoa
    rmin = det + rhoa
    if rmaj < 0:
        raise ValueError("major axis lower than 0.0")
    if rmin < 0:
        raise ValueError("minor axis lower than 0.0")
    rmaj = max(0.0, rmaj)
    rmin = max(0.0, rmin)
    rmaj = math.sqrt(rmaj)
    rmin = math.sqrt(rmin)
    if rmaj < rmin:
        rmaj, rmin = rmin, rmaj
        rpa += 90

    rpa = (rpa + 900) % 180
    if abs(rmaj) < precision:
        rpa = 0.0
    elif abs(rmin) < precision:
        if abs(rpa - lfpa) > 45.0 and abs(rpa - lfpa) < 135:
            rpa = (rpa + 450.0) % 180.0

    return (rmaj, rmin, rpa)
