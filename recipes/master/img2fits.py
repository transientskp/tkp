from __future__ import with_statement
from contextlib import contextmanager

import os
import sys

import lofarpipe.support.lofaringredient as ingredient
from lofarpipe.support.baserecipe import BaseRecipe
from lofarpipe.support.remotecommand import ComputeJob
from lofarpipe.support.remotecommand import RemoteCommandRecipeMixIn

import tkp.utility.fits
import tkp.config


class img2fits(BaseRecipe, RemoteCommandRecipeMixIn):
    """Simple recipe to convert CASA image to FITS files"""

    inputs = {
        'images': ingredient.ListField(
            '--images',
            help="List of images, specified as 2-tuples of "
            "(image name, MS name) ",
        ),
        'results_dir': ingredient.DirectoryField(
            '--results-dir',
            help="Directory in which resulting images will be placed",
            default="."
        ),
        'combine': ingredient.DirectoryField(
            '--combine',
            help="Combination method",
            default="average"
        ),
        'nproc': ingredient.IntField(
            '--nproc',
            help="Maximum number of simultaneous processes per compute node",
            default=8
        ),
        }
       
    outputs = {
        'fitsfiles': ingredient.ListField(),
        'combined_fitsfile': ingredient.FileField(),
        }

    def go(self):
        self.logger.info("Converting CASA images to FITS")
        super(img2fits, self).go()
        self.outputs['fitsfiles' ] = []

        #                        Convert each image to FITS, and supply metadata
        # ----------------------------------------------------------------------
        command = "python %s" % (self.__file__.replace('master', 'nodes'))
        for host, image, ms in self.inputs['images']:
            jobs = []
            fitsfile = os.path.join(
                self.inputs['results_dir'],
                os.path.basename(os.path.splitext(image)[0] + ".fits"))
            self.outputs['fitsfiles'].append(fitsfile)
            jobs.append(
                ComputeJob(
                    host, command,
                    arguments=[
                        image,
                        ms,
                        fitsfile,
                        tkp.config.CONFIGDIR
                        ]
                    )
                )
            jobs = self._schedule_jobs(jobs, max_per_node=self.inputs['nproc'])

        combined_fitsfile = os.path.join(self.inputs['results_dir'], 'combined.fits')
        tkp.utility.fits.combine(self.outputs['fitsfiles'], combined_fitsfile,
                                 method=self.inputs['combine'])
        self.outputs['combined_fitsfile'] = combined_fitsfile
        
        #                Check if we recorded a failing process before returning
        # ----------------------------------------------------------------------
        if self.error.isSet():
            self.logger.warn("Failed imager process detected")
            return 1
        else:
            return 0

if __name__ == '__main__':
    sys.exit(img2fits().main())
