from pylab import *
import pyrap.quanta as qa
import pyrap.tables as pt
import pyrap.measures as pm
from pyrap.measures import measures

targets = [ {'name' : 'CasA', 'ra' : 6.123487680622104,  'dec' : 1.0265153995604648},
            {'name' : 'CygA', 'ra' : 5.233686575770755,  'dec' : 0.7109409582180791},
            {'name' : 'TauA', 'ra' : 1.4596748493730913, 'dec' : 0.38422502335921294},
            {'name' : 'HerA', 'ra' : 4.4119087330382163, 'dec' : 0.087135562905816893},
            {'name' : 'VirA', 'ra' : 3.276086511413598,  'dec' : 0.21626589533567378},
            {'name' : 'SUN'},
            {'name' : 'JUPITER'}]


def check(accessor):

    # The measures object is our interface to pyrap
    m = measures()

    # First, you need to set the reference frame -- ie, the time and the position
    # -- used for the calculations to come.

    # Specify time as MJD in seconds. You could read this from eg the
    # OBSERVATION_START column in the LOFAR_OBSERVATION table.
    #m.do_frame(m.epoch("UTC", "4859435434s"))

    starttime = accessor.taustart_ts
    m.do_frame(m.epoch("UTC", starttime.strftime("%s") + "s"))

    # Specify the position in ITRF (ie, Earth-centred Cartesian) coordinates. You
    # can read this from the telescopeposition entry in the image's coords record;
    # it should be something like the below.
    #m.do_frame(m.position("ITRF", "3826577m", "461023m", "5064893m"))

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
    #pointing = m.direction("J2000", "-2.56847889rad",  "0.91162037rad")

    pointing = m.direction("J2000", "%srad" % accessor.centre_ra,  "%srad"  % accessor.centre_decl)

    # Next, specify the position of your source. For solar system objects note
    # that the RA & dec change with time, but pyrap can handle that based on the
    # time you specified above.
    sun = m.direction("SUN")

    # Alternatively you can specify a position yourself:
    cas_A = m.direction("J2000", "6.123487680622104rad",  "1.0265153995604648rad")

    # Now getting the sepration is easy. In degrees:
    print m.separation(pointing, sun).get_value("deg")

    # Or in radians:
    print m.separation(pointing, cas_A).get_value("rad")
