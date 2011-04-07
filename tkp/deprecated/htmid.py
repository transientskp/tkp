#
# LOFAR Transients Key Project
#
# Code provided by Thijs Coenen, April 2007.
# Calculates HTMIDs in various different ways.
# NB: The TKP pipeline no longer uses HTMIDs; this code is deprecated.
#

from random import randrange, random
from math import floor, ceil, sqrt, sin, cos
pi = 3.141592653589793238462643383279502884197169399

def RA2angle(RA):
    # input right ascension:  (hours, minutes, seconds)
    # output angle in radians
    return ((RA[0] / 12.) + (RA[1] / 720.) + (RA[2] / 43200.)) * pi

def angle2RA(angle):
    # input angle in radians
    # output right ascension:  (hours, minutes, seconds)
    unroundedHours = 12 * angle / (pi)
    hours = int(floor(unroundedHours))
    unroundedMinutes = 60 * (unroundedHours - hours)
    minutes = int(floor(unroundedMinutes))
    unroundedSeconds = 60 * (unroundedMinutes - minutes)
    return (hours, minutes, unroundedSeconds)

def dec2angle(dec):
    # input declination: (degrees, minutes, seconds)
    # output angle (zero at north pole, 90 degrees at southpole) in radians
    return ((90 - dec[0]) / 180. - (dec[1] + dec[2] / 60.) / 10800) * pi



def angle2dec(angle):
    # input angle in radians
    # output right ascension:  (hours, minutes, seconds)
    # goor en lelijk, verbeter (geklooi met +- 90 verschuiving en floor / ceil !)
    unroundedDegrees = 180 * (angle / pi)
    if unroundedDegrees < 0:
        degrees = int(floor(unroundedDegrees))
    else:
        degrees = int(ceil(unroundedDegrees))
    unroundedMinutes = 60 * (unroundedDegrees - degrees)
    minutes = int(ceil(unroundedMinutes))
    unroundedSeconds = 60 * (unroundedMinutes - minutes)
    return (-degrees+90, -minutes, -unroundedSeconds)

def innerproduct(vec1, vec2):
    return vec1[0]*vec2[0] + vec1[1] * vec2[1] + vec1[2] * vec2[2]

def crossproduct(vec1, vec2):
    out0 = vec1[1] * vec2[2] - vec1[2] * vec2[1]
    out1 = vec1[2] * vec2[0] - vec1[0] * vec2[2]
    out2 = vec1[0] * vec2[1] - vec1[1] * vec2[0]
    return (out0, out1, out2)

def inTriangle(v0, v1, v2, testVector):
    # smarter tests would not hurt --- that is test also for 0
    # which means the vector is on a edge or even vertex (two edges)
    a = innerproduct(testVector, crossproduct(v0, v1))
    b = innerproduct(testVector, crossproduct(v1, v2))
    c = innerproduct(testVector, crossproduct(v2, v0))
    #if ((a > 2e-10) and (b > 2e-10)) and (c > 2e-10):
    if ((a > 0) and (b > 0)) and (c > 0):
        return True
    else:
     #   print a,b,c
        return False

def RA2RA(degrees):
    if not (0 <= degrees <= 360):
        raise ValueError, "Right Ascension out of range!"
    return (degrees / 180.) * pi

def dec2dec(degrees):
    if not (-90 <= degrees <= +90):
        raise ValueError, "Declination out of range!"
    return ((-degrees + 90) / 180.) * pi

    
def curse2(v0, v1, v2, testVector, depth):
    if depth == 0:
        return ""
    else:
        h0 = v1[0] + v2[0]
        h1 = v1[1] + v2[1]
        h2 = v1[2] + v2[2]
        h = (h0, h1, h2)
        normFactor = sqrt(innerproduct(h,h))
        w0 = (h0 / normFactor, h1 / normFactor, h2 / normFactor)
        #-------------------
        h0 = v0[0] + v2[0]
        h1 = v0[1] + v2[1]
        h2 = v0[2] + v2[2]
        h = (h0, h1, h2)
        normFactor = sqrt(innerproduct(h,h))
        w1 = (h0 / normFactor, h1 / normFactor, h2 / normFactor)
        #-------------------
        h0 = v0[0] + v1[0]
        h1 = v0[1] + v1[1]
        h2 = v0[2] + v1[2]
        h = (h0, h1, h2)
        normFactor = sqrt(innerproduct(h,h))
        w2 = (h0 / normFactor, h1 / normFactor, h2 / normFactor)    
        # niet normaliseren werkt niet als optimalisatie, geval niet numeriek stabiel

        test1 = innerproduct(testVector, crossproduct(w0, w1))
        test2 = innerproduct(testVector, crossproduct(w1, w2))
        test3 = innerproduct(testVector, crossproduct(w2, w0))
        if test1 < 0:
            return "2" + curse2(v2, w1, w0, testVector, depth -1)
        elif test2 < 0:
            return "0" + curse2(v0, w2, w1, testVector, depth -1)
        elif test3 < 0:
            return "1" + curse2(v1, w0, w2, testVector, depth -1)
        else:
            return "3" + curse2(w0, w1, w2, testVector, depth -1)
    
def narf(theta, phi, depth):
    if not (0 <= theta <= pi):
        raise ValueError, "Declination out of range"
    if not (0 <= phi <= 2*pi):
        print phi
        raise ValueError, "Right Ascension out of range"
    testVector = (sin(theta) * cos(phi), sin(theta) * sin(phi), cos(theta))
    #testVector = (sin(theta) * cos(pi/4), sin(theta) * sin(pi/4), cos(theta))
    #testVector = (0.7071067811865476, 0.7071067811865475, 0.0)
    #print testVector
    v0 = (0, 0, 1)
    v1 = (1, 0, 0)
    v2 = (0, 1, 0)
    v3 = (-1, 0, 0)
    v4 = (0, -1, 0)
    v5 = (0, 0, -1)
    if inTriangle(v1, v5, v2, testVector):
        return "S0" + curse2(v1, v5, v2, testVector, depth)
    elif inTriangle(v2, v5, v3, testVector):
        return "S1" + curse2(v2, v5, v3, testVector, depth)
    elif inTriangle(v3, v5, v4, testVector):
        return "S2" + curse2(v3, v5, v4, testVector, depth)
    elif inTriangle(v4, v5, v1, testVector):
        return "S3" + curse2(v4, v5, v1, testVector, depth)
    elif inTriangle(v1, v0, v4, testVector):
        return "N0" + curse2(v1, v0, v4, testVector, depth)
    elif inTriangle(v4, v0, v3, testVector):
        return "N1" + curse2(v4, v0, v3, testVector, depth)
    elif inTriangle(v3, v0, v2, testVector):
        return "N2" + curse2(v3, v0, v2, testVector, depth)
    elif inTriangle(v2, v0, v1, testVector):
        return "N3" + curse2(v2, v0, v1, testVector, depth)
    else:
        raise ValueError, "Vector lies on the edge of two triangular cells."

def narf2(theta, phi, depth):
    if not (0 <= theta <= pi):
        raise ValueError, "Declination out of range"
    if not (0 <= phi <= 2*pi):
        print phi
        raise ValueError, "Right Ascension out of range"
    testVector = (sin(theta) * cos(phi), sin(theta) * sin(phi), cos(theta))
    b0 = (0, 0, 1)
    b1 = (1, 0, 0)
    b2 = (0, 1, 0)
    b3 = (-1, 0, 0)
    b4 = (0, -1, 0)
    b5 = (0, 0, -1)
    if inTriangle(b1, b5, b2, testVector):
        output = "S0"
        v0 = b1
        v1 = b5
        v2 = b2
    elif inTriangle(b2, b5, b3, testVector):
        output = "S1"
        v0 = b2
        v1 = b5
        v2 = b3
    elif inTriangle(b3, b5, b4, testVector):
        output = "S2"
        v0 = b3
        v1 = b5
        v2 = b4
    elif inTriangle(b4, b5, b1, testVector):
        output = "S3"
        v0 = b4
        v1 = b5
        v2 = b1
    elif inTriangle(b1, b0, b4, testVector):
        output = "N0"
        v0 = b1
        v1 = b0
        v2 = b4
    elif inTriangle(b4, b0, b3, testVector):
        output = "N1"
        v0 = b4
        v1 = b0
        v2 = b3
    elif inTriangle(b3, b0, b2, testVector):
        output = "N2"
        v0 = b3
        v1 = b0
        v2 = b2
    elif inTriangle(b2, b0, b1, testVector):
        output = "N3"
        v0 = b2
        v1 = b0
        v2 = b1
    else:
        raise ValueError, "Vector lies on the edge of two triangular cells."

    while depth > 0:
        h0 = v1[0] + v2[0]
        h1 = v1[1] + v2[1]
        h2 = v1[2] + v2[2]
        h = (h0, h1, h2)
        normFactor = sqrt(innerproduct(h,h))
        w0 = (h0 / normFactor, h1 / normFactor, h2 / normFactor)
        #-------------------
        h0 = v0[0] + v2[0]
        h1 = v0[1] + v2[1]
        h2 = v0[2] + v2[2]
        h = (h0, h1, h2)
        normFactor = sqrt(innerproduct(h,h))
        w1 = (h0 / normFactor, h1 / normFactor, h2 / normFactor)
        #-------------------
        h0 = v0[0] + v1[0]
        h1 = v0[1] + v1[1]
        h2 = v0[2] + v1[2]
        h = (h0, h1, h2)
        normFactor = sqrt(innerproduct(h,h))
        w2 = (h0 / normFactor, h1 / normFactor, h2 / normFactor)    
        # niet normaliseren werkt niet als optimalisatie, geval niet numeriek stabiel

        test1 = innerproduct(testVector, crossproduct(w0, w1))
        test2 = innerproduct(testVector, crossproduct(w1, w2))
        test3 = innerproduct(testVector, crossproduct(w2, w0))
        if test1 < 0:
            output += "2" 
            v0 = v2
            v1 = w1
            v2 = w0
        elif test2 < 0:
            output += "0"
            v0 = v0
            v1 = w2
            v2 = w1
        elif test3 < 0:
            output += "1"
            v0 = v1
            v1 = w0
            v2 = w2
        else:
            output += "3"
            v0 = w0
            v1 = w1
            v2 = w2
        depth -= 1
    return output

    
def narf3(theta, phi, depth):
    if not (0 <= theta <= pi):
        raise ValueError, "Declination out of range"
    if not (0 <= phi <= 2*pi):
        print phi
        raise ValueError, "Right Ascension out of range"
    testVector = (sin(theta) * cos(phi), sin(theta) * sin(phi), cos(theta))
    b0 = [0, 0, 1]
    b1 = [1, 0, 0]
    b2 = [0, 1, 0]
    b3 = [-1, 0, 0]
    b4 = [0, -1, 0]
    b5 = [0, 0, -1]
    if inTriangle(b1, b5, b2, testVector):
        output = 8
        v0 = b1
        v1 = b5
        v2 = b2
    elif inTriangle(b2, b5, b3, testVector):
        output = 9
        v0 = b2
        v1 = b5
        v2 = b3
    elif inTriangle(b3, b5, b4, testVector):
        output = 10
        v0 = b3
        v1 = b5
        v2 = b4
    elif inTriangle(b4, b5, b1, testVector):
        output = 11
        v0 = b4
        v1 = b5
        v2 = b1
    elif inTriangle(b1, b0, b4, testVector):
        output = 12
        v0 = b1
        v1 = b0
        v2 = b4
    elif inTriangle(b4, b0, b3, testVector):
        output = 13
        v0 = b4
        v1 = b0
        v2 = b3
    elif inTriangle(b3, b0, b2, testVector):
        output = 14
        v0 = b3
        v1 = b0
        v2 = b2
    elif inTriangle(b2, b0, b1, testVector):
        output = 15
        v0 = b2
        v1 = b0
        v2 = b1
    else:
        raise ValueError, "Vector lies on the edge of two triangular cells."

    while depth > 0:
        h0 = v1[0] + v2[0]
        h1 = v1[1] + v2[1]
        h2 = v1[2] + v2[2]
        h = (h0, h1, h2)
        normFactor = sqrt(innerproduct(h,h))
        w0 = (h0 / normFactor, h1 / normFactor, h2 / normFactor)
        #-------------------
        h0 = v0[0] + v2[0]
        h1 = v0[1] + v2[1]
        h2 = v0[2] + v2[2]
        h = (h0, h1, h2)
        normFactor = sqrt(innerproduct(h,h))
        w1 = (h0 / normFactor, h1 / normFactor, h2 / normFactor)
        #-------------------
        h0 = v0[0] + v1[0]
        h1 = v0[1] + v1[1]
        h2 = v0[2] + v1[2]
        h = (h0, h1, h2)
        normFactor = sqrt(innerproduct(h,h))
        w2 = (h0 / normFactor, h1 / normFactor, h2 / normFactor)    
        # niet normaliseren werkt niet als optimalisatie, geval niet numeriek stabiel

        test1 = innerproduct(testVector, crossproduct(w0, w1))
        test2 = innerproduct(testVector, crossproduct(w1, w2))
        test3 = innerproduct(testVector, crossproduct(w2, w0))
        if test1 < 0:
            output = (output << 2) + 2 
            v0 = v2
            v1 = w1
            v2 = w0
        elif test2 < 0:
            output = output << 2
            v0 = v0
            v1 = w2
            v2 = w1
        elif test3 < 0:
            output = (output << 2) + 1
            v0 = v1
            v1 = w0
            v2 = w2
        else:
            output = (output << 2) + 3
            v0 = w0
            v1 = w1
            v2 = w2
        depth -= 1
    return output

    
        
def coord2HTM(theta, phi, depth):
    if not (0 <= theta <= pi):
        raise ValueError, "Declination out of range"
    if not (0 <= phi <= 2*pi):
        print phi
        raise ValueError, "Right Ascension out of range"
    testVector = (sin(theta) * cos(phi), sin(theta) * sin(phi), cos(theta))
    #testVector = (sin(theta) * cos(pi/4), sin(theta) * sin(pi/4), cos(theta))
    #testVector = (0.7071067811865476, 0.7071067811865475, 0.0)
    #print testVector
    v0 = (0, 0, 1)
    v1 = (1, 0, 0)
    v2 = (0, 1, 0)
    v3 = (-1, 0, 0)
    v4 = (0, -1, 0)
    v5 = (0, 0, -1)
    if inTriangle(v1, v5, v2, testVector):
        return "S0" + curse(v1, v5, v2, testVector, depth)
    elif inTriangle(v2, v5, v3, testVector):
        return "S1" + curse(v2, v5, v3, testVector, depth)
    elif inTriangle(v3, v5, v4, testVector):
        return "S2" + curse(v3, v5, v4, testVector, depth)
    elif inTriangle(v4, v5, v1, testVector):
        return "S3" + curse(v4, v5, v1, testVector, depth)
    elif inTriangle(v1, v0, v4, testVector):
        return "N0" + curse(v1, v0, v4, testVector, depth)
    elif inTriangle(v4, v0, v3, testVector):
        return "N1" + curse(v4, v0, v3, testVector, depth)
    elif inTriangle(v3, v0, v2, testVector):
        return "N2" + curse(v3, v0, v2, testVector, depth)
    elif inTriangle(v2, v0, v1, testVector):
        return "N3" + curse(v2, v0, v1, testVector, depth)
    else:
        raise ValueError, "Vector lies on the edge of two triangular cells."

def curse(v0, v1, v2, testVector, depth):
    #-------------------
    h0 = v1[0] + v2[0]
    h1 = v1[1] + v2[1]
    h2 = v1[2] + v2[2]
    h = (h0, h1, h2)
    normFactor = sqrt(innerproduct(h,h))
    w0 = (h0 / normFactor, h1 / normFactor, h2 / normFactor)
    #-------------------
    h0 = v0[0] + v2[0]
    h1 = v0[1] + v2[1]
    h2 = v0[2] + v2[2]
    h = (h0, h1, h2)
    normFactor = sqrt(innerproduct(h,h))
    w1 = (h0 / normFactor, h1 / normFactor, h2 / normFactor)
    #-------------------
    h0 = v0[0] + v1[0]
    h1 = v0[1] + v1[1]
    h2 = v0[2] + v1[2]
    h = (h0, h1, h2)
    normFactor = sqrt(innerproduct(h,h))
    w2 = (h0 / normFactor, h1 / normFactor, h2 / normFactor)    
    #-------------------
    if depth > 0:
        if inTriangle(v0, w2, w1, testVector):
            return "0" + curse(v0, w2, w1, testVector, depth -1)
        elif inTriangle(v1, w0, w2, testVector):
            return "1" + curse(v1, w0, w2, testVector, depth -1)
        elif inTriangle(v2, w1, w0, testVector):
            return "2" + curse(v2, w1, w0, testVector, depth -1)
        elif inTriangle(w0, w1, w2, testVector):
            return "3" + curse(w0, w1, w2, testVector, depth -1)
        else:
            depth = 0
            raise ValueError, "Vector lies of the edge of two triangular cells."
    else:
        return ""

def HTMstring2number(htm_string):
    o = 0
    if len(htm_string) > 1:
        if htm_string[0] == "N":
            o += 3
        else:
            o += 2
        for i in range(1, len(htm_string)):
            o = o * 4
            o += int(htm_string[i])
    return o

def _runtest():
    import sys
    if len(sys.argv) == 4:
        depth = int(sys.argv[1])
        ra = RA2RA(float(sys.argv[2]))
        dec = dec2dec(float(sys.argv[3]))

        a = coord2HTM(dec, ra, depth)
        a2 = narf2(dec, ra, depth)
        n = HTMstring2number(a)
        n2 = HTMstring2number(a2)
        print a, "  ", n
        print "te vergelijken met >>>>>>>>>>>\n"
        print a2, "  ", n2
        #print narf3(dec, ra, depth)
        print "                     ", "  ", narf3(dec, ra, depth)
    else:
        print "Input should be as follows: coord2htm <recursion depth> <Right Ascension in degrees> <declination in degrees>"

if __name__ == "__main__":
    _runtest()
