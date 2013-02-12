import logging
import warnings
import pyrap.quanta as qa
from pyrap.measures import measures
from tkp.utility.coordinates import unix2julian

logger = logging.getLogger(__name__)

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

    #TODO: this function should be split up and tested more atomically

    if accessor.position == None:
        msg = "image doesn't have position metadata. " \
                "can't check if bright source is near"
        logger.warning(msg)
        warnings.warn(msg)
        return False

    # The measures object is our interface to pyrap
    m = measures()

    # First, you need to set the reference frame -- ie, the time and the
    # position -- used for the calculations to come. Time as MJD in seconds.
    starttime = int(accessor.taustart_ts.strftime("%s"))
    starttime_mjd = unix2julian(starttime)
    m.do_frame(m.epoch("UTC", "%ss" % starttime_mjd))

    x = qa.quantity(accessor.position[0], 'm')
    y = qa.quantity(accessor.position[1], 'm')
    z = qa.quantity(accessor.position[2], 'm')
    position = m.position('ITRF', x, y, z)
    m.doframe(position)

    # Second, you need to set your image pointing.
    pointing = m.direction(
        "J2000", "%sdeg" % accessor.centre_ra,  "%sdeg"  % accessor.centre_decl
    )

    for name, position in targets.items():
        if not position:
            direction = m.direction(name)
        else:
            direction = m.direction(
                "J2000", "%srad" % position['ra'], "%srad" % position['dec']
            )
        separation = m.separation(pointing, direction).get_value("deg")
        if separation < distance:
            return "Pointing is %s degrees from %s." % (separation, name)
    return False
