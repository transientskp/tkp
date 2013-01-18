"""
This script is used to inject missing header info into a FITS file or CASA
table. his can be useful to make your data processable by the TRAP pipeline.
"""

import sys
import os.path
import argparse
from lofarpipe.support.parset import parameterset
import pyfits
from pyrap.tables import table as pyrap_table
import tkp.utility.accessors.detection
from tkp.utility.accessors.lofarcasaimage import LofarCasaImage
from tkp.utility.accessors.fitsimage import FitsImage

type_mapping = {
    str: 'getString',
    int: 'getInt',
    float: 'getFloat',
}

parset_fields = {
    'taustart_ts': (str, 'DATE-OBS'),
    'freq_eff': (float, 'RESTFRQ'),
    'freq_bw': (float, 'RESTBW'),
    'tau_time': (float, 'TAU_TIME'),
    'antenna_set': (str, 'ANTENNA'),
    'subbands': (int, 'SUBBANDS'),
    'channels': (int, 'CHANNELS'),
    'ncore': (int, 'NCORE'),
    'nremote': (int, 'NREMOTE'),
    'nintl': (int, 'NINTL'),
    'position': (int, 'POSITION'),
    'subbandwidth': (float, 'SUBBANDW'),
    'bmaj': (float, 'BMAJ'),
    'bmin': (float, 'BMIN'),
    'bpa': (float, 'BPA'),
}

extra_doc = " Properties which can be overwritten or set in the parset file are: " +\
    ", ".join(parset_fields.keys())

def parse_arguments():
    parser = argparse.ArgumentParser(description=__doc__ + extra_doc)
    parser.add_argument('parsetfile', help='path to parset file')
    parser.add_argument('targetfile', help='path to FITS/CASA file to manipulate', nargs='+')
    parsed = parser.parse_args()
    parsetfile = os.path.expanduser(parsed.parsetfile)
    targetfiles = map(os.path.expanduser, parsed.targetfile)
    return parsetfile, targetfiles

def parse_parset(path):
    parsed = {}
    parset = parameterset(path)
    for name, (type_, fits_field) in parset_fields.items():
        getter = getattr(parset, type_mapping[type_])
        try:
            value = getter(name)
            parsed[name] = value
        except RuntimeError:
            pass # value not defined in parset file, continue
    return parsed

def modify_fits_headers(parset, fits_file):
    hdu = 0 # Header Data Unit, usually 0
    fits_file = pyfits.open(fits_file, mode='update')
    header = fits_file[0].header
    for parset_field, (type_, fits_field) in parset_fields.items():
        if parset.has_key(parset_field):
            value = parset[parset_field]
            print "setting %s (%s) to %s" % (parset_field, fits_field, value)
            header[fits_field] = value
    fits_file.flush()
    fits_file.close()

def modify_casa_headers(parset, casa_file):
    table = pyrap_table(casa_file, ack=False)
    origin_location = table.getkeyword("ATTRGROUPS")['LOFAR_ORIGIN']
    origin_table = pyrap_table(origin_location, ack=False, readonly=False)

    for parset_field, value in parset.items():
        if parset_field == 'tau_time':
            tau_time = value
            print "setting tau_time to %s" % (tau_time)
            starttime = origin_table.getcell('START', 0)
            entime = starttime + tau_time
            origin_table.putcell('END', 0, entime)
        else:
            print "WARNING: this script does not support setting %s for a CASA table" % parset_field
    origin_table.close()
    table.close()

def main():
    parset_file, target_files = parse_arguments()
    parset = parse_parset(parset_file)

    for target_file in target_files:
        print "injecting data into %s" % target_file
        accessor_class = tkp.utility.accessors.detection.detect(target_file)

        if accessor_class == FitsImage:
            modify_fits_headers(parset, target_file)
        elif accessor_class == LofarCasaImage:
            modify_casa_headers(parset, target_file)
        else:
            print "ERROR: %s is in a unknown format" % target_file
