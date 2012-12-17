from pylab import *
import pyrap.quanta as qa
from pyrap.measures import measures
from tkp.utility.coordinates import unix2julian

targets = { 'CasA': {'ra' : 6.123487680622104,  'dec' : 1.0265153995604648},
            'CygA': {'ra' : 5.233686575770755,  'dec' : 0.7109409582180791},
            'TauA': {'ra' : 1.4596748493730913, 'dec' : 0.38422502335921294},
            'HerA': {'ra' : 4.4119087330382163, 'dec' : 0.087135562905816893},
            'VirA': {'ra' : 3.276086511413598,  'dec' : 0.21626589533567378},
            'SUN': None,
            'JUPITER': None,
        }


def is_bright_source_near(accessor, distance=20):
    """ Checks if there is any of the bright radio sources defined in targets
    near the center of the image.
    Args:
        accessor: a TKP accessor
        distance: maximum allowed distance of a bright source (in degrees)
    Returns:
        False if not bright source is near, description of source if a bright
         source is near
    """
    # The measures object is our interface to pyrap
    m = measures()

    # First, you need to set the reference frame -- ie, the time and the position
    # -- used for the calculations to come. Time as MJD in seconds. 
    starttime = int(accessor.taustart_ts.strftime("%s"))
    starttime_mjd = unix2julian(starttime)
    m.do_frame(m.epoch("UTC", "%ss" % starttime_mjd))

    # Specify the position in ITRF (ie, Earth-centred Cartesian) coordinates. You
    # can read this from the telescopeposition entry in the image's coords record;
    ant_table = accessor.subtables['LOFAR_ANTENNA']
    ant_no = 0
    pos = ant_table.getcol('POSITION')
    x = qa.quantity( pos[ant_no,0], 'm' )
    y = qa.quantity( pos[ant_no,1], 'm' )
    z = qa.quantity( pos[ant_no,2], 'm' )
    position =  m.position( 'ITRF', x, y, z )
    m.doframe( position )

    # Second, you need to set your image pointing. You should get Antonia to
    # define exactly what the "image pointing" means, but I suspect you could read
    # this from the pointingcenter entry in the image's coords record. You can
    # specify it in a range of different coordinate systems, but probably J2000 RA
    # & dec is most useful. You can use whatever angle representation you like
    # (degrees, radians...), but the coords record stores in radians so I guess
    # that's easiest.
    pointing = m.direction("J2000", "%srad" % accessor.centre_ra,  "%srad"  % accessor.centre_decl)

    for name, position in targets.items():
        if not position:
            direction = m.direction(name)
        else:
            direction = m.direction("J2000", "%srad" % position['ra'], "%srad" % position['dec'])
        seperation = m.separation(pointing, direction).get_value("deg")
        if seperation < distance:
            return "Pointing is %s degrees from %s." % (seperation, name)