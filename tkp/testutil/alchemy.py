from datetime import datetime, timedelta
import tkp.db

def gen_band(central=150**6, low=None, high=None):
    if not low:
        low = central * .9
    if not high:
        high = central * 1.1
    return tkp.db.model.Frequencyband(freq_low=low, freq_central=central,
                                      freq_high=high)


def gen_dataset(description):
    return tkp.db.model.Dataset(process_start_ts=datetime.now(),
                                description=description)


def gen_skyregion(dataset):
    return tkp.db.model.Skyregion(dataset=dataset, centre_ra=1, centre_decl=1,
                                  xtr_radius=1, x=1, y=1, z=1)


def gen_image(band, dataset, skyregion, taustart_ts=None):
    if not taustart_ts:
        taustart_ts = datetime.now()
    return tkp.db.model.Image(band=band, dataset=dataset, skyrgn=skyregion,
                              freq_eff=2, rb_smin=1, taustart_ts=taustart_ts,
                              rb_smaj=1, rb_pa=1, deltax=1, deltay=1, rms_qc=0)


def gen_extractedsource(image):
    return tkp.db.model.Extractedsource(zone=1, ra=1, decl=1, uncertainty_ew=1, x=1, y=1,
                                        z=1, uncertainty_ns=1, ra_err=1, decl_err=1,
                                        ra_fit_err=1, decl_fit_err=1, ew_sys_err=1,
                                        ns_sys_err=1, error_radius=1, racosdecl=1,
                                        det_sigma=1, f_int=0.01, image=image)


def gen_runningcatalog(xtrsrc, dataset):
    return tkp.db.model.Runningcatalog(xtrsrc=xtrsrc, dataset=dataset, datapoints=1,
                                       zone=1, wm_ra=1., wm_decl=1, wm_uncertainty_ew=1,
                                       wm_uncertainty_ns=1, avg_ra_err=1, avg_decl_err=1,
                                       avg_wra=1, avg_wdecl=1, avg_weight_ra=1, avg_weight_decl=1,
                                       x=1, y=1, z=1)
def gen_assocskyrgn(runcat, skyrgn):
    return tkp.db.model.Assocskyrgn(runcat=runcat, skyrgn=skyrgn,
                                    distance_deg=10)


def gen_assocxtrsource(runningcatalog, xtrsrc):
    return tkp.db.model.Assocxtrsource(runcat=runningcatalog, xtrsrc=xtrsrc,
                                       type=0, r=0, distance_arcsec=0, v_int=0,
                                       eta_int=0, f_datapoints=0)


def gen_newsource(runcat, xtrsrc, image):
    return tkp.db.model.Newsource(runcat=runcat, trigger_xtrsrc=xtrsrc,
                                  newsource_type=1, previous_limits_image=image)


def gen_lightcurve(band, dataset, skyregion, datapoints=10):
    """
    returns: a list of created SQLAlchemy objects
    """
    start = datetime.fromtimestamp(0)
    ten_sec = timedelta(seconds=10)
    xtrsrcs = []
    images = []
    assocs = []
    for i in range(datapoints):
        taustart_ts = start + ten_sec * i
        image = gen_image(band, dataset, skyregion, taustart_ts)

        if i == 5:
            image.int = 10
        images.append(image)
        xtrsrcs.append(gen_extractedsource(image))

    # now we can make runningcatalog, we use first xtrsrc as trigger src
    runningcatalog = gen_runningcatalog(xtrsrcs[0], dataset)
    assocskyrgn = gen_assocskyrgn(runningcatalog, skyregion)

    # create the associations. Can't do this directly since the
    # association table has non nullable columns
    for xtrsrc in xtrsrcs:
        assocs.append(gen_assocxtrsource(runningcatalog, xtrsrc))

    newsource = gen_newsource(runningcatalog, xtrsrcs[5], images[4])

    # just return all db objects we created
    return [dataset, band, skyregion, runningcatalog, assocskyrgn, newsource] + \
           images + xtrsrcs + assocs