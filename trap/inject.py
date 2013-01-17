"""
This script is used to inject missing header info into a FITS file. his can
be useful to make a FITS file processable by the TRAP pipeline.
"""

import os.path
import argparse
from lofarpipe.support.parset import parameterset
import pyfits

type_mapping = {
    str: 'getString',
    int: 'getInt',
    float: 'getFloat',
}

parset_fields = {
    'taustart_ts': (str, 'DATE-OBS'),
    'freq_eff': (float, 'RESTFRQ'),
    'freq_bw': (float, 'RESTBW'),
    'endtime': (str, 'END_UTC'),
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
    #'tau_time': (float, '??'
    #'centre_decl': (float,
    #'centre_ra': (float,
}

extra_doc = " Properties which can be overwritten in the parset file are: " +\
    ", ".join(parset_fields.keys())

def parse_arguments():
    parser = argparse.ArgumentParser(description=__doc__ + extra_doc)
    parser.add_argument('parsetfile', help='path to parset file')
    #parser.add_argument('filefile', nargs=argparse.REMAINDER)
    parser.add_argument('fitsfile', help='path to FITS file to manipulate')
    parsed = parser.parse_args()
    return map(os.path.expanduser, (parsed.parsetfile, parsed.fitsfile))


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


def modify_headers(parset, fits_file):
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


def main():
    parset_file, fits_file = parse_arguments()
    parset = parse_parset(parset_file)
    modify_headers(parset, fits_file)

