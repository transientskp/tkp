import os
from tkp.config import config as tkp_conf
import datetime
import logging
from collections import namedtuple

ExtractedSourceTuple = namedtuple("ExtractedSourceTuple",
                                ['ra', 'dec' ,
                                'ra_err' , 'dec_err' ,
                                'peak' , 'peak_err',
                                'flux', 'flux_err',
                                 'sigma',
                                 'beam_maj', 'beam_min',
                                 'beam_angle'
                                ])

def use_test_database_by_default():
    test_db_name = tkp_conf['test']['test_database_name']
    tkp_conf['database']['name'] = test_db_name
    tkp_conf['database']['user'] = test_db_name
    tkp_conf['database']['password'] = test_db_name

def delete_test_database(database):
    """
    Use with caution!

    NB. Not the same as a freshly initialised database.
        All the sequence counters are offset.
    """
    import monetdb.sql
    if database.name.lower().find("test") != 0:
        raise ValueError("You tried to delete a database not prefixed with 'test'.\n"
                         "Not recommended!")
    try:
        cursor = database.connection.cursor()
        query = "DELETE from monitoringlist"
        cursor.execute(query)
        query = "DELETE from runningcatalog_flux"
        cursor.execute(query)
        query = "DELETE from assocxtrsource"
        cursor.execute(query)
        query = "DELETE from temprunningcatalog"
        cursor.execute(query)
        query = "DELETE from runningcatalog"
        cursor.execute(query)
        query = "DELETE from extractedsource"
        cursor.execute(query)
        query = "DELETE from image"
        cursor.execute(query)
        query = "DELETE from dataset"
        cursor.execute(query)
        query = "DELETE from transient"
        cursor.execute(query)
        if not tkp_conf['database']['autocommit']:
            database.connection.commit()
    except monetdb.sql.Error:
        logging.warn("Query failed when trying to blank database\n"
                     "Query: " + query)
        raise
    finally:
        cursor.close()


def example_dbimage_datasets(n_images):
    """Generate a list of image data dictionaries.

    These can be used to create known entries in the image table.
    """
    starttime = datetime.datetime(2012, 1, 1) #Happy new year
    time_spacing = datetime.timedelta(seconds=600)

    init_im_params = {'tau_time':300,
                      'freq_eff':140e6,
                      'freq_bw':2e6,
                      'taustart_ts':starttime,
                      'url':"someurl"}

    im_params = []
    for i in range(n_images):
        im_params.append(init_im_params.copy())
        init_im_params['taustart_ts'] += time_spacing

    return im_params

def example_extractedsource_tuple(ra=123.123, dec=10.5,
                                  ra_err=5. / 3600, dec_err=6. / 3600,
                                  peak=15e-3, peak_err=5e-4,
                                  flux=15e-3, flux_err=5e-4,
                                  sigma=15,
                                  beam_maj=100, beam_min=100,
                                  beam_angle=45):
    # NOTE: ra_err & dec_err are in degrees (they are converted to arcsec in the db)
    return ExtractedSourceTuple(ra=ra, dec=dec, ra_err=ra_err, dec_err=dec_err,
                                peak=peak, peak_err=peak_err,
                                flux=flux, flux_err=flux_err,
                                sigma=sigma,
                                beam_maj=beam_maj, beam_min=beam_min,
                                beam_angle=beam_angle
                               )


#Used to record the significance levels on a lightcurve.    
MockLCPoint = namedtuple('MockLightCurvePoint',
                                 'index peak flux sigma')

#NB To do: The `MockSource` class is very quick and dirty, currently.
#A little refinement here would probably go a long way.
class MockSource(object):
    """Defines a MockSource for generating mock source lists.

    (These can be used to test the database routines.)
    """
    def __init__(self,
                 ex,
                 lightcurve=None,
                 ):
        """
        *Args*
        `ex`: template `extractedsource`, Defines the position, etc.
        If no lightcurve is supplied, then these details are used to  model a
        fixed source.

        `lightcurve`: A list of `MockLightcurvePoint`s, defining a transient
                        lightcurve.
        """
        self.ex = ex
        self.lc = lightcurve

        if self.lc is not None:
            for p1 in self.lc:
                for p2 in self.lc:
                    if (p1.index == p2.index) and (p1 is not p2):
                        raise ValueError("Two lightcurve points supplied for same"
                                        "image index.")

    def value_at_image(self, image_index):
        """Returns an `extractedsource` for a given image index.

        If no lightcurve was supplied, always returns fixed details.

        If lightcurve present, then check for a defined lightcurve point.
        Otherwise, return the template details with peak, flux, sigma all set
        to zero.
        """
        if self.lc is None:
            return self.ex
        else:
            for p in self.lc:
                if p.index == image_index:
                    return self.ex._replace(peak=p.peak,
                                            flux=p.flux,
                                            sigma=p.sigma)
            return self.ex._replace(peak=0, flux=0, sigma=0)


def example_source_lists(n_images, include_non_detections,
                         non_detection_sigma_threshold=0.0):
    """
        Return source lists for more than 7 images, 1 fixed source, 3 transients.

        Mock sources are as follows:
            1 Fixed source, present in all lists returned.
            2 `fast transients`
                1 present in images[3], sigma = 15
                1 present in images[4], sigma = 5
            1 `slow transient`,
                present in images indices [5]  (sigma = 4) and [6], (sigma = 3)

       NB To do: The `MockSource` class is very quick and dirty, currently.
            A little refinement here would probably go a long way.
    """
    assert n_images >= 7



    FixedSource = MockSource(example_extractedsource_tuple(ra=123.123, dec=10.5))


    WeakSlowTransient = MockSource(example_extractedsource_tuple(ra=123.888, dec=10.5),
                lightcurve=[MockLCPoint(index=5, peak=4e-3, flux=4e-3, sigma=4),
                            MockLCPoint(index=6, peak=3e-3, flux=3e-3, sigma=3),
                            ])

    BrightFastTransient = MockSource(
                         example_extractedsource_tuple(ra=123.888, dec=15.666),
                         lightcurve=[MockLCPoint(index=3, peak=30e-3,
                                                   flux=30e-3, sigma=30)
                                     ])

    WeakFastTransient = MockSource(
                         example_extractedsource_tuple(ra=123.000, dec=15.666),
                         lightcurve=[MockLCPoint(index=4, peak=5e-3,
                                                   flux=5e-3, sigma=5)
                                     ])

    all_sources = [FixedSource, WeakSlowTransient, BrightFastTransient,
                   WeakFastTransient]

    for s1 in all_sources:
            for s2 in all_sources:
                if (s1.ex.ra == s2.ex.ra and
                    s1.ex.dec == s2.ex.dec and
                    s1 is not s2):
                    raise ValueError("Oops - Your source list"
                                    "contains two superimposed sources.")

    img_source_lists = []
    for i in range(n_images):
        l = []
        for s in all_sources:
            ex = s.value_at_image(i)
            if include_non_detections:
                l.append(ex)
            else:
                if ex.sigma > non_detection_sigma_threshold:
                    l.append(ex)
        img_source_lists.append(l)

    return img_source_lists
