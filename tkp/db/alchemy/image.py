import math
from datetime import datetime
import tkp.db
from tkp.db.model import Frequencyband, Skyregion, Image, Dataset
from tkp.utility.coordinates import eq_to_cart
from sqlalchemy import func, cast
from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION as Double

insert_freqband_query = """
insert into frequencyband
(dataset
,freq_central
,freq_low
,freq_high
)
values
(%(dataset)s
,%(freq_central)s
,%(freq_low)s
,%(freq_high)s
)
"""
get_freqband_query = """
select id
  from frequencyband
 where dataset = %(dataset)s
   and (greatest(%(high)s, freq_high) - least(%(low)s, freq_low))
       <
       (%(freq_bw)s + (freq_high - freq_low))
limit 1
"""

def get_bandid(session, dataset, freq_eff, freq_bw, freq_bw_max=.0):
    """
    Returns the frequency band for the given frequency parameters. Will create a new frequency band entry in the
    database if no match is found. You can limit the bandwidth of the band association with the freq_bw_max.

    args:
        session (sqlalchemy.orm.session.Session): a SQLAlchemy session object
        dataset (tkp.db.model.Dataset): the TraP dataset
        freq_eff (float): The central frequency of image to get band for
        freq_bw (float): The bandwidth of image to get band for
        freq_bw_max (float): The maximum bandwith used for band association. Not used if 0.0 (default).

    returns:
        tkp.db.model.Frequencyband: a frequency band object
    """

    if freq_bw_max == .0:
        bw_half = freq_bw / 2
        low = freq_eff - bw_half
        high = freq_eff + bw_half
    else:
        bw_half = freq_bw_max / 2
        low = freq_eff - bw_half
        high = freq_eff + bw_half

    w1 = high - low
    w2 = Frequencyband.freq_high - Frequencyband.freq_low
    max_ = func.greatest(high, Frequencyband.freq_high)
    min_ = func.least(low, Frequencyband.freq_low)

    #print "But now check this: vvvvvvvvvvv"
    params = {'dataset': dataset.id
             ,'low': low
             ,'high': high
             ,'freq_bw': freq_bw}
    cursor = tkp.db.execute(get_freqband_query, params, commit=True)
    results = cursor.fetchall()
    #print "results = %s" % (results)
    if len(results) == 0:
        bandid = None
    else:
        bandid = results[0][0]
    #print "A bandid = %s" % (bandid)
    #print "What about that?? ^^^^^^^^^^^^^^^^"

    if not bandid:
        params = {'dataset': dataset.id
                 ,'freq_central': freq_eff
                 ,'freq_low': low
                 ,'freq_high': high
                 }
        #print "freqband params = %s" % (params)
        #print "freqband ins query = %s" % (insert_freqband_query % params)
        cursor = tkp.db.execute(insert_freqband_query, params, commit=True)
        bandid = cursor.lastrowid

    #print "B bandid = %s" % (bandid)
    return bandid

def update_skyregionid_members(session, skyregionid, xtr_radius):
    """
    This function performs a simple distance-check against current members of the
    runningcatalog to find sources that should be visible in the given skyregion,
    and updates the assocskyrgn table accordingly.

    Any previous entries in assocskyrgn relating to this skyregion are
    deleted first.

    Note 1. We use the variable 'inter' to cache the extraction_radius as transformed
    onto the unit sphere, so this does not have to be recalculated for every
    comparison.

    Note 2. (To Do:) This distance check could be made more efficient by
    restricting to a range of RA values, as we do with the Dec.
    However, this optimization is complicated by the meridian wrap-around issue.
        """
    inter = 2. * math.sin(math.radians(xtr_radius) / 2.)
    inter_sq = inter * inter

    params = {'inter_sq': inter_sq
             ,'skyregion_id': skyregionid
             }
    q = """
      INSERT INTO assocskyrgn
        (
        runcat
        ,skyrgn
        ,distance_deg
        )
      SELECT rc.id as runcat
            ,sky.id as skyrgn
            ,DEGREES(2 * ASIN(SQRT( (rc.x - sky.x) * (rc.x - sky.x)
                                    + (rc.y - sky.y) * (rc.y - sky.y)
                                    + (rc.z - sky.z) * (rc.z - sky.z)
                                  ) / 2 )
                     )
        FROM skyregion sky
            ,runningcatalog rc
       WHERE sky.id = %(skyregion_id)s
         AND rc.dataset = sky.dataset
         AND rc.wm_decl BETWEEN sky.centre_decl - sky.xtr_radius
                            AND sky.centre_decl + sky.xtr_radius
         AND (  (rc.x - sky.x) * (rc.x - sky.x)
                + (rc.y - sky.y) * (rc.y - sky.y)
                + (rc.z - sky.z) * (rc.z - sky.z)
             ) < %(inter_sq)s
      ;
    """
    tkp.db.execute(q, params, commit=True)
    return inter

insert_skyregion_query = """
INSERT INTO skyregion
(dataset
,centre_ra
,centre_decl
,xtr_radius
,x
,y
,z
)
VALUES
(%(dataset)s
,%(centre_ra)s
,%(centre_decl)s
,%(xtr_radius)s
,%(x)s
,%(y)s
,%(z)s
)
"""

select_skyregion_query = """
select id
  from skyregion
 where dataset = %(dataset)s
   and centre_ra = %(centre_ra)s
   and centre_decl = %(centre_decl)s
   and xtr_radius = %(xtr_radius)s
limit 1
"""

def get_skyregionid(session, dataset, centre_ra, centre_decl, xtr_radius):
    """
     gets an id for a skyregion, given a pair of central co-ordinates and a radius.

     If no matching skyregion is found, a new one is inserted. In this case we also trigger execution of
     `updateSkyRgnMembers` for the new skyregion - this performs a simple assocation with current members of the
     runningcatalog to find sources that should be visible in the new skyregion, and updates the assocskyrgn table
     accordingly.

     args:
        session (sqlalchemy.orm.session.Session): a SQLAlchemy session object
        dataset_id (int): the dataset ID
        centre_ra (float): center RA coordinate
        centre_decl (float): center DECL coordinate
        xtr_radius (float): The extraction radius

     returns:
        tkp.db.models.Skyregion: a SQLalchemy skyregion
     """
    params = {'dataset': dataset.id
             ,'centre_ra': centre_ra
             ,'centre_decl': centre_decl
             ,'xtr_radius': xtr_radius
             }
    cursor = tkp.db.execute(select_skyregion_query, params, commit=True)
    results = cursor.fetchall()
    if len(results) == 0:
        skyregionid = None
    else:
        skyregionid = results[0][0]

    if not skyregionid:
        x, y, z = eq_to_cart(centre_ra, centre_decl)
        params = {'dataset': dataset.id
                 ,'centre_ra': centre_ra
                 ,'centre_decl': centre_decl
                 ,'xtr_radius': xtr_radius
                 ,'x': x
                 ,'y': y
                 ,'z': z
                 }
        cursor = tkp.db.execute(insert_skyregion_query, params, commit=True)
        skyregionid = cursor.lastrowid

        skyregion = Skyregion(id=skyregionid)
        update_skyregionid_members(session, skyregionid, xtr_radius)

    return skyregionid

insert_image_query = """
insert into image
(dataset
,band
,skyrgn
,tau_time
,freq_eff
,freq_bw
,taustart_ts
,rb_smaj
,rb_smin
,rb_pa
,deltax
,deltay
,rms_qc
,rms_min
,rms_max
,detection_thresh
,analysis_thresh
,url
)
values
(%(dataset)s
,%(band)s
,%(skyrgn)s
,%(tau_time)s
,%(freq_eff)s
,%(freq_bw)s
,%(taustart_ts)s
,%(rb_smaj)s
,%(rb_smin)s
,%(rb_pa)s
,%(deltax)s
,%(deltay)s
,%(rms_qc)s
,%(rms_min)s
,%(rms_max)s
,%(detection_thresh)s
,%(analysis_thresh)s
,%(url)s
)
"""

def insert_image(session, dataset, freq_eff, freq_bw, taustart_ts, tau_time, beam_smaj_pix, beam_smin_pix,
                 beam_pa_rad, deltax, deltay, url, centre_ra, centre_decl, xtr_radius, rms_qc, freq_bw_max=0.0,
                 rms_min=None, rms_max=None, detection_thresh=None, analysis_thresh=None):
    """
    Insert an image for a given dataset.

    Args:
        session (sqlalchemy.orm.session.Session): A SQLalchemy sessions
        dataset (int): ID of parent dataset.
        freq_eff: See :ref:`Image table definitions <schema-image>`.
        freq_bw: See :ref:`Image table definitions <schema-image>`.
        freq_bw_max (float): Optional override for freq_bw, not used if 0.
        taustart_ts: See :ref:`Image table definitions <schema-image>`.
        taus_time: See :ref:`Image table definitions <schema-image>`.
        beam_smaj_pix (float): Restoring beam semimajor axis length in pixels.
            (Converted to degrees before storing to database).
        beam_smin_pix (float): Restoring beam semiminor axis length in pixels.
            (Converted to degrees before storing to database).
        beam_pa_rad (float): Restoring beam parallactic angle in radians.
            (Converted to degrees before storing to database).
        deltax(float): Degrees per pixel increment in x-direction.
        deltay(float): Degrees per pixel increment in y-direction.
        centre_ra(float): Image central RA co-ord, in degrees.
        centre_decl(float): Image central Declination co-ord, in degrees.
        xtr_radius(float): Radius in degrees from field centre that will be used
            for source extraction.

    """
    # this looks a bit weird, but this simplifies backwards compatibility
    dataset_id = dataset
    dataset = Dataset(id=dataset_id)

    skyrgnid = get_skyregionid(session, dataset, centre_ra, centre_decl, xtr_radius)
    skyrgn = Skyregion(id=skyrgnid)

    bandid = get_bandid(session, dataset, freq_eff, freq_bw, freq_bw_max)
    band = Frequencyband(id=bandid)
    rb_smaj = beam_smaj_pix * math.fabs(deltax)
    rb_smin = beam_smin_pix * math.fabs(deltay)
    rb_pa = 180 * beam_pa_rad / math.pi

    args = ['dataset', 'band', 'tau_time', 'freq_eff', 'freq_bw', 'taustart_ts', 'skyrgn', 'rb_smaj', 'rb_smin',
            'rb_pa', 'deltax', 'deltay', 'url', 'rms_qc', 'rms_min', 'rms_max', 'detection_thresh', 'analysis_thresh']

    l = locals()
    kwargs = {arg: l[arg] for arg in args}
    image = Image(**kwargs)
    params = {'dataset': dataset.id
             ,'band': bandid
             ,'skyrgn': skyrgnid
             ,'tau_time': kwargs['tau_time']
             ,'freq_eff': kwargs['freq_eff']
             ,'freq_bw': kwargs['freq_bw']
             ,'taustart_ts': kwargs['taustart_ts'].strftime("%Y-%m-%d %H:%M:%S")
             ,'rb_smaj': kwargs['rb_smaj']
             ,'rb_smin': kwargs['rb_smin']
             ,'rb_pa': kwargs['rb_pa']
             ,'deltax': kwargs['deltax']
             ,'deltay': kwargs['deltay']
             ,'rms_qc': kwargs['rms_qc']
             ,'rms_min': kwargs['rms_min']
             ,'rms_max': kwargs['rms_max']
             ,'detection_thresh': kwargs['detection_thresh']
             ,'analysis_thresh': kwargs['analysis_thresh']
             ,'url': kwargs['url']
             }
    cursor = tkp.db.execute(insert_image_query, params, commit=True)
    imageid = cursor.lastrowid
    return imageid

def insert_dataset(session, description):
    rerun = session.query(func.max(Dataset.rerun)). \
        select_from(Dataset).  \
        filter(Dataset.description == "description"). \
        one()[0]

    if not rerun:
        rerun = 0
    else:
        rerun += 1

    dataset = Dataset(rerun=rerun,
                      process_start_ts=datetime.now(),
                      description=description)
    session.add(dataset)
    return dataset
