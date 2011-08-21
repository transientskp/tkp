# -*- coding: utf-8 -*-
#import tkp.sourcefinder.accessors as access
#import tkp.sourcefinder.image as imag
import sys
import os



import tkp.utility.accessors as access
import tkp.sourcefinder.image as imag
import tkp.sourcefinder.utils as util
from  optparse  import OptionParser # deprecated in Python2.7 


writeNoiseMaps = True

parser = OptionParser()
parser.add_option("-n", help= "write noise files", action= "store_true", dest= "writeNoiseMaps")
#code expects a single arg  - a full path to the fits files to be processed
fp = sys.argv[1:]

if   not fp:
    print "Please enter file path to directory of files(.fits) for processing"
else:
     fpt = fp[0]
try:
    # get a list of fits files for processing
    res = os.listdir(fpt)
except OSError:
    print "Directory path error " , fp
    sys.exit()
#loop processing each fits file
for fname in res:
    ext = os.path.splitext(fname)[1]
    if ext  ==".fits":
        fpath  =os.path.join(fpt, fname)
        if not os.path.isdir(fpath):
            try:
                my_fitsfile = access.FitsFile(fpath)
                print "processing ", fpath, " ", my_fitsfile # may be removed ...marks progress
                my_image = access.sourcefinder_image_from_accessor(my_fitsfile)
                sextract_results = my_image.extract()
                fnm= os.path.splitext(fpath)[0]
                name = os.path.split(fnm)[1]
                filepath = fnm +".reg"
                textpath = fnm + ".txt"
                ds9file = open (filepath, "w")
                ds9file.write('\nglobal color=white font=\"helvetica 10 normal\" select=1 highlite=1 edit=1 move=1 delete=1 include=1 fixed=0 source')
                ds9file.write('\nIMAGE;')
                resultfile = open(textpath, "w")
                for sources in sextract_results:
                    sources.printob(resultfile)
                    ds9file.write(sources.printasregion())
                ds9file.close();
 
                if writeNoiseMaps:
                    derived  = os.path.join(fp, "deriveFits")
                    if not os.path.isdir(derived) :
                        os.makedirs(derived)
                    npath = os.path.join(derived, name)
                    print npath
                    noisepathB =  npath + "backg.fits"
                    noisepathRMS = npath+ "rms.fits"
                    islpath = npath+ "src.fits"
                    header = my_fitsfile.get_header()
                    my_fitsfile.writefits(my_image.rmsmap, noisepathRMS, header)
                    my_fitsfile.writefits(my_image.backmap, noisepathB, header)
                    my_fitsfile.writefits(my_image.islands_map, islpath, header)
                my_image.clearcache();    
            except IOError :
                print "skipping file ", fname
            except ValueError:
                print "Value missing skipping file ", fname
    


#if __name__ == '__main__':
   


