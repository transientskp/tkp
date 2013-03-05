import os
import datetime
import logging
from collections import namedtuple
from tkp.config import config as tkp_conf
from tkp.database.database import DataBase
from tkp.database.orm import DataSet, Image
import tkp.testutil.data as testdata

ExtractedSourceTuple = namedtuple("ExtractedSourceTuple",
                                ['ra', 'dec' ,
                                 'ra_fit_err' , 'dec_fit_err' ,
                                 'peak' , 'peak_err',
                                 'flux', 'flux_err',
                                 'sigma',
                                 'beam_maj', 'beam_min', 'beam_angle',
                                 'ra_sys_err', 'dec_sys_err'
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
        query = "DELETE from assocskyrgn"
        cursor.execute(query)
        query = "DELETE from temprunningcatalog"
        cursor.execute(query)
        query = "DELETE from transient"
        cursor.execute(query)
        query = "DELETE from runningcatalog"
        cursor.execute(query)
        query = "DELETE from extractedsource"
        cursor.execute(query)
        query = "DELETE from image"
        cursor.execute(query)
        query = "DELETE from skyregion"
        cursor.execute(query)
        query = "DELETE from dataset"
        cursor.execute(query)
        if not tkp_conf['database']['autocommit']:
            database.connection.commit()
    except monetdb.sql.Error:
        logging.warn("Query failed when trying to blank database\n"
                     "Query: " + query)
        raise
    finally:
        cursor.close()


def example_dbimage_datasets(n_images, **kwargs):
    """Generate a list of image data dictionaries.

    These can be used to create known entries in the image table.
    """
    starttime = datetime.datetime(2012, 1, 1) #Happy new year
    time_spacing = datetime.timedelta(seconds=600)

    init_im_params = {'tau_time':300,
                      'freq_eff':140e6,
                      'freq_bw':2e6,
                      'taustart_ts':starttime,
                      'beam_smaj_pix': float(2.7),
                      'beam_smin_pix': float(2.3),
                      'beam_pa_rad': float(1.7),
                      'deltax': float(-0.01111),
                      'deltay': float(0.01111),
                      'url':testdata.fits_file, # just an arbitrary existing fits file
                      'centre_ra': 123.,
                      'centre_decl': 10.,
                      'xtr_radius' : 10. # (Degrees)
                    }
    init_im_params.update(kwargs)

    im_params = []
    for i in range(n_images):
        im_params.append(init_im_params.copy())
        init_im_params['taustart_ts'] += time_spacing

    return im_params

def example_extractedsource_tuple(ra=123.123, dec=10.5,
                                  ra_fit_err=5. / 3600, dec_fit_err=6. / 3600,
                                  peak=15e-3, peak_err=5e-4,
                                  flux=15e-3, flux_err=5e-4,
                                  sigma=15,
                                  beam_maj=100, beam_min=100, beam_angle=45,
                                  ra_sys_err=20, dec_sys_err=20):
    # NOTE: ra_fit_err & dec_fit_err are in degrees (they are converted to arcsec in the db),
    # and ra_sys_err & decl_sys_err are in arcsec.
    # The ra_err is then the sqrt of the quadratic sum
    return ExtractedSourceTuple(ra=ra, dec=dec,
                                ra_fit_err=ra_fit_err, dec_fit_err=dec_fit_err,
                                peak=peak, peak_err=peak_err,
                                flux=flux, flux_err=flux_err,
                                sigma=sigma,
                                beam_maj=beam_maj, beam_min=beam_min,
                                beam_angle=beam_angle,
                                ra_sys_err=ra_sys_err, dec_sys_err=dec_sys_err
                               )


#Used to record the significance levels on a lightcurve.    
MockLCPoint = namedtuple('MockLightCurvePoint',
                                 'index peak flux sigma')

#NB To do: The `MockSource` class is very quick and dirty, currently.
#A little refinement here would probably go a long way.
class MockSource(object):
    """Defines a MockSource for generating mock source lists.

    (These can be used to test the database routines.)

    When initialised with a transient lightcurve (a list of MockLCPoint tuples),
    the source lists can be populated with non-detections (zero measurements)
    at the images for which the lightcurve is not defined.

    When the lightcurve is not provided, the extractedsource tuple serves as
    the basis for a fixed source.
    A list of identical measurements will then be generated for the required
    number of images.

    This makes it much easier to easily generate source lists for testing
    the database!

     See also: `example_source_lists` for a usage example.

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

    def synthesise_measurements(self, n_images, include_non_detections,
                                non_detection_sigma_threshold=None):
        """Return a list of measurements corresponding to images.

        If include_non_detections is false, then images where the lightcurve
        falls below the threshold are represented by a 'None' element
        in the list.

        """

        if include_non_detections is False:
            if non_detection_sigma_threshold is None:
                raise ValueError('Must supply a non-detection threshold '
                 'when synthesising a patchy lightcurve.')

        measurements = []
        for i in xrange(n_images):
            ex = self.value_at_image(i)
            if include_non_detections:
                measurements.append(ex)
            else:
                if ex.sigma > non_detection_sigma_threshold:
                    measurements.append(ex)
                else:
                    measurements.append(None)
        assert len(measurements) == n_images
        return measurements


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
        img_source_lists.append([])

    for s in all_sources:
        measurements = s.synthesise_measurements(n_images,
                                                 include_non_detections,
                                                 non_detection_sigma_threshold)
        for index, m in enumerate(measurements):
            if m is not None:
                img_source_lists[index].append(m)
    return img_source_lists


def create_dataset_8images(database=False, extract_sources=False):
    """
    creates a fake dataset with 8 images
    returns: dataset database id
    """
    if not database:
        database = DataBase()
    dataset = DataSet(data={'description': 'testdataset'}, database=database)
    n_images = 8
    db_imgs = []
    im_params = example_dbimage_datasets(n_images)
    source_lists = example_source_lists(n_images=8, include_non_detections=True)
    for i in xrange(n_images):
        db_imgs.append(Image(data=im_params[i], dataset=dataset))
        if extract_sources:
            db_imgs[i].insert_extracted_sources(source_lists[i])
            db_imgs[i].associate_extracted_sources(deRuiter_r=3.7)
    return dataset.id
