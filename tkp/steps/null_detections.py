

from tkp.utility.parset import Parset as parameterset


def parse_parset(parset_file):
    parset = parameterset(parset_file)
    return {
        'backsize_x': parset.getInt('backsize_x'),
        'backsize_y': parset.getInt('backsize_y'),
        'margin': parset.getFloat('margin'),
        'deblend': parset.getBool('deblend'),
        'deblend_nthresh': parset.getInt('deblend_nthresh'),
        'radius': parset.getFloat('radius'),
        'ra_sys_err': parset.getFloat('ra_sys_err'),
        'dec_sys_err': parset.getFloat('dec_sys_err'),
        'detection_threshold': parset.getFloat('detection_threshold'),
        'analysis_threshold': parset.getFloat('analysis_threshold'),
        'force_beam': parset.getBool('force_beam', False),
        'association_radius': parset.getFloat('association_radius'),
        'deRuiter_radius': parset.getFloat('deRuiter_radius'),
        'bg-density': parset.getFloat('bg-density'),
        'box_in_beampix': parset.getBool('box_in_beampix', 10),
    }
