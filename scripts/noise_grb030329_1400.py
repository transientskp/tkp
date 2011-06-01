
import tkp_lib.accessors as access
import tkp_lib.dataset as ds
import tkp_lib.image as imag
import tkp_lib.coordinates as coords

import pyfits as p
import time
import math

start=time.time()
# path='/home/claw/survey/images/whole_int/'
path='/home/bscheers/maps/grb030329/fits//'
# masterfile='L3464_cal_ch_cl3k.fits'
masterfile='GRB030329_WSRT_20040129_1400.fits'
#masterfile='GRB030329_WSRT_20050409_1400.fits'
# masterfile='UVMIN2PBC_2048_2000.FITS'
# path='/home/hspreeuw/repo/pipe/python-packages/tkp_lib/tests/data/L15_12h_const/'
# masterfile='model-all.fits'
d = ds.DataSet('create nois maps')
my_fitsfile = access.FitsFile(path+masterfile)

my_image= imag.ImageData(my_fitsfile, dataset=d)
# print 'tot hier'
# my_sr=my_image.extract()
#extract_results = my_image.extract()
extract_results = my_image.extract(det=150,anl=10)
einde=time.time()
print 'len(extract_results)=',len(extract_results)
# fluxes = []
i=0
for detection in extract_results:
      # print 'peak',detection.peak,'ra',detection.ra,'dec',detection.dec
      i+=1
      # print 'ra,error=',coords.ratohms(detection.ra.value),detection.ra.error*3600.,'dec,error=',\
      # coords.dectodms(detection.dec.value),detection.dec.error*3600.,'theta,error=',detection.theta_celes,\
      # 'semi-major axis=',detection.smaj_asec.value,'semi-minor axis=',detection.smin_asec.value,\
      # 'theta_pixels=',math.degrees(detection.theta.value)
print 'total number of sources=',i
# i=1
# for obj in my_sr.Island:
#    print i,obj.serialize()
#     i+=1
# for detection in my_sr.detections:
# print my_sr

print 'It took',einde-start,'seconds to extract and measure the sources in this map.'
hdu=p.PrimaryHDU(my_image.rmsmap.swapaxes(0,1))
print 'minimum and maximum noise:',my_image.rmsmap.min(),my_image.rmsmap.max()
hdu.writeto('noise_from_' + masterfile)
hdu=p.PrimaryHDU(my_image.backmap.swapaxes(0,1))
print 'minimum and maximum background:',my_image.backmap.min(),my_image.backmap.max()
hdu.writeto('background_from_' + masterfile)

# hdu=p.PrimaryHDU(my_image.residuals_from_Gauss_fitting.swapaxes(0,1))
# hdu.writeto('residuals_from_Gauss_fitting_from_tkp_lib_not_WENSS.FITS')
# hdu=p.PrimaryHDU(my_image.residuals_from_deblending.swapaxes(0,1))
# hdu.writeto('residuals_from_deblending_from_tkp_lib_not_WENSS.FITS')
# hdu=p.PrimaryHDU(my_image.sources_intact.swapaxes(0,1))
# hdu.writeto('sources_intact_from_tkp_lib_not_WENSS.FITS')
# hdu=p.PrimaryHDU(my_image.sources_deblended.swapaxes(0,1))
# hdu.writeto('sources_deblended_from_tkp_lib_not_WENSS.FITS')
