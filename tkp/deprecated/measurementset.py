#
# LOFAR Transients Key Project
#
# Interface to AIPS++ MeasurementSet data.
#

#######################################################
#                                                     #
# This code is deprecated, and probably doesn't work! #
#                                                     #
#######################################################

import shutil, os, tempfile
import pycasa
import mako.template, mako.lookup
import dataset
# Our working directory
from tkp_lib import __path__ as librarypath

class measurementset(object):
    """Class for working with & imaging MeasurementSets"""
    def __init__(self, path, masterfile):
        self.path = path
        self.masterfile = masterfile
        if (not path) or (not masterfile):
            raise 'path & masterfile must be defined'
        if not os.access(path + masterfile, os.R_OK and os.W_OK and os.X_OK):
            raise 'Measurement set not accessible'
        self.glish_lookup = mako.lookup.TemplateLookup(directories=[librarypath[0] + '/glish_templates'], module_directory='/tmp/mako_modules')

    def start_time(self):
        tab = pycasa.table(self.path + self.masterfile)
        time = tab.getcol('TIME')
        del tab
        return time[0]
        
    def end_time(self):
        tab = pycasa.table(self.path + self.masterfile)
        time = tab.getcol('TIME')
        del tab
        return time[-1]

    def time_step(self):
        tab = pycasa.table(self.path + self.masterfile)
        time = tab.getcol('TIME')
        del tab
        for i in range(len(time)):   # more than one row per time, so need to find where time flips to next integration.  assumes times are in order.
            if time[i] != time[i+1]:
                break
        return time[i+1]-time[i]

    def length(self):
        return self.end_time() - self.start_time()

    def select_data(self, start_time, end_time, filename, verbose=True):
# option 1:  there seems to be a bug in the table copying.  commented out for now, it may work without this copy step...
#        tab = pycasa.table(self.path + self.masterfile, False)
#        tab.taql('select from $1 where TIME <= ' + str(end_time) + ' and TIME >= ' + str(start_time) + ' giving ' + self.path + filename + '.tmp')
#        self.__execute_glish('dataset.select_data.tmpl', {'path':self.path, 'filename':filename}, verbose=verbose)
#        shutil.rmtree(self.path + filename + '.tmp')

# option 2:  alternative that doesn't work for cutting subsets of data
#        self.__execute_glish('dataset.select_data2.tmpl', {'path':self.path, 'masterfile':self.masterfile, 'start_time':start_time, 'end_time':end_time, 'filename':filename}, verbose=verbose)
#        shutil.rmtree(self.path + filename + '.tmp')

# option 3:  new pycasa deepcopy option (that doesn't really work)
#        tab = pycasa.table(self.path + self.masterfile, False)
#        tab2 = tab.taql('select from $1 where TIME <= ' + str(end_time) + ' and TIME >= ' + str(start_time))
#        tab2.deepcopy(self.path + filename)

# option 4:  Use aips++ split command.  Note that it works on integration numbers, not time.
        whichcol = "CORRECTED_DATA"
        start_time_rel = int(start_time-self.start_time())
        end_time_rel = int(end_time-self.start_time())
#        start_time_int = int((start_time-self.start_time())/self.time_step())
#        end_time_int = int((end_time-self.start_time())/self.time_step())
#        print 'start time and relative start time',start_time,start_time_rel
#        print 'end time and relative end time',end_time,end_time_rel
        self.__execute_glish('dataset.select_data3.tmpl', {'path':self.path, 'masterfile':self.masterfile, 'start_time':start_time_rel, 'end_time':end_time_rel, 'filename':filename, 'whichcol':whichcol}, verbose=verbose)

        return measurementset(self.path, filename)

    def make_image(self, filename=False, verbose=True, **user_params):
        # Always 'dirty' images for now; generates both and AIPS++ image & a FITS file.
        # Returns a FitsFile object pointing to the latter.
    
        # image_params contains a complete set of default values for *both*
        # single-shot and averaged imaging. Those which aren't used by your
        # current method are ignored. Override them in the function arguments.
        # It's up to you to know which are required by your particular chunk
        # o' glish.
        image_params = {'fieldid':1, 'totspwid':1, 'startspwid':1, 'spwid':1,
            'totchan':9, 'startchan':99, 'outchan':1, 'imagechanstep':10, 
            'npix':2880, 'cellsize':'120arcsec', 'ra_phasecenter':'23h21m10', 
            'dec_phasecenter':'58d32m16', 'min_baseline_squared':2500, 'niter':2000, 
            'gain':0.05, 'threshold':'2Jy', 'path':self.path, 'masterfile':self.masterfile,
            'averaged':False, 'imagetype':'observed'}

        try:
            image_params.update(user_params)
        except:
            pass

        if filename:
            tempfits = False
            image_params['filename'] = filename
        else:
            tempfits = True
            image_params['filename'] = tempfile.mktemp()

        self.__execute_glish('dataset.make_image.tmpl', image_params, verbose=verbose)

        return dataset.FitsFile(image_params['filename'], tempfits)

    def __execute_glish(self, glishname, arguments, verbose=True):
        mytemplate = self.glish_lookup.get_template(glishname)
        tmpname = tempfile.mktemp()
        tmp = open(tmpname, 'w')
        tmp.writelines(mytemplate.render(**arguments))
        tmp.close()

        # execute script
        import subprocess
        try:
            if verbose:
                returncode = subprocess.call(('glish', '-l', tmpname), stdout=None)
            else:
                returncode = subprocess.call(('glish', '-l', tmpname), stdout=subprocess.PIPE)
        finally:
            os.remove(tmpname)
        if returncode != 0:
            raise OSError, "glish exited with code " + str(returncode)


