import pyfits,numpy

#filename = '/home/bscheers/maps/grb030329/fits/GRB030329_06MAR08.USB.PBCOR.FITS'
filename = '/home/bscheers/maps/grb030329/fits/GRB030329_WSRT_20031225_1400.fits'
#filename = '/home/bscheers/maps/wenss/fits/WN30218H'
hdulist = pyfits.open(filename)
prthdr = hdulist[0].header

xpix_deg = prthdr['CDELT1']
ypix_deg = prthdr['CDELT2']

print "ra pix incr:", abs(float(xpix_deg))
print "dec pix incr:", abs(float(ypix_deg))

try:
    bmaj = prthdr['BMAJ']
    bmin = prthdr['BMIN']
    bpa = prthdr['BPA']
except KeyError:
    # it must be a fits file reduced with aips
    found = False
    for i in range(len(prthdr.ascardlist().keys())):
        if (prthdr.ascardlist().keys()[i] == 'HISTORY'):
            histline = prthdr[i]
            if (histline.find('BMAJ') > -1):
                found = True
                idx_bmaj = histline.find('BMAJ')
                idx_bmin = histline.find('BMIN')
                idx_bpa = histline.find('BPA')
                bmaj = float(histline[idx_bmaj+5:idx_bmin]) 
                bmin = float(histline[idx_bmin+5:idx_bpa])
                bpa = float(histline[idx_bpa+4:len(histline)])
    if (found == False):
        print "no beam size info could be found"
        raise KeyError


print "bmaj", bmaj, "[degrees]"
print "bmin", bmin, "[degrees]"
print "bpa", bpa, "[degrees]"

semimaj_pix = (bmaj / 2) / abs(float(xpix_deg)) 
semimin_pix = (bmin / 2) / abs(float(ypix_deg)) 
theta = numpy.pi * bpa / 180

print "semimaj:", round(semimaj_pix,1), "[pix]"
print "semimin:", round(semimin_pix,1), "[pix]"
print "theta:", theta, "[rad]"

