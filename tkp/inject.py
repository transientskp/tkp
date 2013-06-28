"""
This script is used to inject missing header info into a FITS file or CASA
table. This can be useful to make your data processable by the TRAP pipeline.
"""

import os.path
import argparse
import pyfits
from pyrap.tables import table as pyrap_table
import tkp.utility.accessors.detection
from tkp.utility.accessors import LofarFitsImage, LofarCasaImage
from  tkp.utility.parset import read_config_section

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
    'subbandwidth': (float, 'SUBBANDW'),
    'bmaj': (float, 'BMAJ'),
    'bmin': (float, 'BMIN'),
    'bpa': (float, 'BPA'),
    'itrf_position_x': (float, 'ITRFPOSX'),
    'itrf_position_y': (float, 'ITRFPOSY'),
    'itrf_position_z': (float, 'ITRFPOSZ'),
}

extra_doc = " Properties which can be overwritten or set in the parset file are: " + \
    ", ".join(parset_fields.keys())

def parse_arguments():
    parser = argparse.ArgumentParser(description=__doc__ + extra_doc)
    parser.add_argument('parsetfile', help='path to parset file')
    parser.add_argument('targetfile', help='path to FITS/CASA file to manipulate', nargs='+')
    parser.add_argument('--over', action='store_true', default=False,
                        help='Overwrite header values even if already present. '
                        '(Only applies to FITS files - for CASA tables we always '
                        'set/overwrite tau_time only.)')
    parsed = parser.parse_args()
    parsetfile = os.path.expanduser(parsed.parsetfile)
    targetfiles = map(os.path.expanduser, parsed.targetfile)
    overwrite = parsed.over
    return parsetfile, targetfiles, overwrite


def modify_fits_headers(parset, fits_file, overwrite):
    hdu = 0 # Header Data Unit, usually 0
    fits_file = pyfits.open(fits_file, mode='update')
    header = fits_file[0].header
    already_present = header.keys()
    for parset_field, (type_, fits_field) in parset_fields.items():
        if parset.has_key(parset_field):
            if (fits_field not in already_present) or overwrite:
                value = parset[parset_field]
                print "setting %s (%s) to %s" % (parset_field, fits_field, value)
                header.update(fits_field, value)
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
    parset_file, target_files, overwrite = parse_arguments()
    with open(parset_file) as fp:
        parset = read_config_section(fp, 'inject')

    for target_file in target_files:
        #Normally accessors.open checks this, but we're going straight 
        #to detect here because we don't want to actually open it:
        if not os.path.isfile(target_file) or os.path.isdir(target_file):
            print "File not found: %s (check path is correct?)" % target_file
            continue
        print "injecting data into %s" % target_file
        accessor_class = tkp.utility.accessors.detection.detect(target_file)

        if accessor_class == LofarFitsImage:
            modify_fits_headers(parset, target_file, overwrite)
        elif accessor_class == LofarCasaImage:
            modify_casa_headers(parset, target_file)
        else:
            print "ERROR: %s is in a unknown format" % target_file
