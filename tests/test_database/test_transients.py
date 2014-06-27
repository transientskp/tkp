import unittest
from collections import defaultdict
import tkp.db
from tkp.db.transients import multi_epoch_transient_search
from tkp.db.transients import _insert_variable_source_transients
from tkp.db.generic import get_db_rows_as_dicts
from tkp.db import nulldetections
from tkp.testutil import db_subs
from tkp.testutil.db_subs import (example_extractedsource_tuple,
                                  MockSource,
                                  insert_image_and_simulated_sources,
                                  get_transients_for_dataset)
from tkp.testutil.decorators import requires_database

# Convenient default values
deRuiter_r = 3.7
new_source_sigma_margin = 3

class TestSimplestCases(unittest.TestCase):
    """
    Various basic test-cases of the transient-detection logic.

    In these simple cases we just have one source, fixed image properties,
    and identical min/max image RMS values.

    As a result, we can only test for type 1 / 2 transients here, i.e.
    -type 1: single-epoch, bright enough that we would previously have seen it
        wherever in the image it lies, or
    -type 2: multi-epoch, identified by variability, possibly from forced-fits.

    (Type 0 is a possible single-epoch transient, that might just be a steady
    source fluctuating in a high-RMS region, or might be real transient
    if it's seen in the low-RMS region).

    """

    @requires_database()
    def setUp(self):
        self.database = tkp.db.Database()

        self.dataset = tkp.db.DataSet(database=self.database,
                                data={'description':"Trans:"
                                        + self._testMethodName})
        self.n_images = 4
        self.new_source_sigma_margin = 3
        image_rms = 1e-3
        detection_thresh=10

        self.search_params = dict(eta_lim=1,
                                  V_lim=0.1,
                                  probability_threshold=0.7,
                                  minpoints=1, )

        self.barely_detectable_flux = 1.01*image_rms*(detection_thresh)
        self.reliably_detectable_flux = (
            1.01*image_rms*(detection_thresh+self.new_source_sigma_margin))

        # 1mJy image RMS, 10-sigma detection threshold = 10mJy threshold.
        test_specific_img_params = dict(rms_qc = image_rms,
                                rms_min = image_rms,
                                rms_max = image_rms,
                                detection_thresh = detection_thresh)

        self.im_params = db_subs.generate_timespaced_dbimages_data(
            self.n_images,**test_specific_img_params)

    def tearDown(self):
        tkp.db.rollback()

    def test_steady_source(self):
        """
        Sanity check: Ensure we get no transients for a really steady source.
        """
        im_params = self.im_params
        steady_src = db_subs.MockSource(
             template_extractedsource=db_subs.example_extractedsource_tuple(
                 ra=im_params[0]['centre_ra'],
                 dec=im_params[0]['centre_decl'],
             ),
             lightcurve=defaultdict(lambda : self.reliably_detectable_flux)
        )

        inserted_sources = []
        for img_pars in im_params:
            image, _,forced_fits = insert_image_and_simulated_sources(
                self.dataset,img_pars,[steady_src],
                self.new_source_sigma_margin)

            #should not have any nulldetections
            self.assertEqual(len(forced_fits), 0)

            multi_epoch_transient_search(image_id=image.id,
                                         **self.search_params)
            transients = get_transients_for_dataset(self.dataset.id)

            #or transients
            self.assertEqual(len(transients), 0)


    def test_single_epoch_bright_transient(self):
        """A bright transient appears at field centre in one image."""
        im_params = self.im_params
        transient_src = db_subs.MockSource(
             template_extractedsource=db_subs.example_extractedsource_tuple(
                 ra=im_params[0]['centre_ra'],
                 dec=im_params[0]['centre_decl'],
             ),
             lightcurve={im_params[2]['taustart_ts'] :
                             self.reliably_detectable_flux}
        )

        for img_pars in im_params[:3]:
            image, _,forced_fits = insert_image_and_simulated_sources(
                self.dataset,img_pars,[transient_src],
                self.new_source_sigma_margin)
            self.assertEqual(len(forced_fits), 0)

        # Check the number of detected transients
        transients = get_transients_for_dataset(self.dataset.id)
        self.assertEqual(len(transients), 1)
        transient_properties = transients[0]
        # Check that the bands for the images are the same as the transient's band
        freq_bands = self.dataset.frequency_bands()
        self.assertEqual(len(freq_bands), 1)
        self.assertEqual(freq_bands[0], transient_properties['band'])

        #Sanity check that the runcat is correctly matched
        runcats = self.dataset.runcat_entries()
        self.assertEqual(len(runcats), 1)
        self.assertEqual(runcats[0]['runcat'], transient_properties['runcat'])

        #Since it is a single-epoch source, variability indices default to 0:
        self.assertEqual(transient_properties['v_int'],0)
        self.assertEqual(transient_properties['eta_int'],0)

        #Bright 'new-source' / single-epoch transients have type 1:
        self.assertEqual(transient_properties['transient_type'],1)

        #Check the correct trigger xtrsrc was identified:
        self.assertEqual(transient_properties['taustart_ts'],
                         transient_src.lightcurve.keys()[0])

        # Ok, now add the last image and check that we get a correct forced-fit
        # request:
        image, _,forced_fits = insert_image_and_simulated_sources(
                self.dataset,im_params[3],[transient_src],
                self.new_source_sigma_margin)
        self.assertEqual(len(forced_fits),1)

        #Trigger updating of variability indices
        transients = multi_epoch_transient_search(image_id=image.id,
                                                  **self.search_params)

        #And now we should have a non-zero variability value:
        transients = get_transients_for_dataset(self.dataset.id)
        self.assertEqual(len(transients), 1)
        transient_properties = transients[0]
        # print "\n",transient_properties
        self.assertNotAlmostEqual(transient_properties['v_int'],0)
        self.assertNotAlmostEqual(transient_properties['eta_int'],0)


    def test_single_epoch_weak_transient(self):
        """
        A weak (barely detected in blind extraction) transient appears at
        field centre in one image, then disappears entirely.

        Because it is a weak extraction, it will not be immediately marked
        as transient, but it will get flagged up after forced-fitting due to
        the variability search.
        """
        im_params = self.im_params

        transient_src = db_subs.MockSource(
             template_extractedsource=db_subs.example_extractedsource_tuple(
                 ra=im_params[0]['centre_ra'],
                 dec=im_params[0]['centre_decl'],
             ),
             lightcurve={im_params[2]['taustart_ts'] :
                             self.barely_detectable_flux}
        )

        inserted_sources = []

        for img_pars in im_params[:3]:
            image, _,forced_fits = insert_image_and_simulated_sources(
                self.dataset,img_pars,[transient_src],
                self.new_source_sigma_margin)
            self.assertEqual(forced_fits, [])
            #Trigger updating of variability indices
            transients = multi_epoch_transient_search(image_id=image.id,
                                          **self.search_params)
            transients = get_transients_for_dataset(self.dataset.id)
            self.assertEqual(len(transients), 0)

        #Now, the final, empty image:
        image, blind_extractions, forced_fits = insert_image_and_simulated_sources(
                self.dataset,im_params[3],[transient_src],
                self.new_source_sigma_margin)
        self.assertEqual(len(blind_extractions),0)
        self.assertEqual(len(forced_fits), 1)
        transients = multi_epoch_transient_search(image_id=image.id,
                                                  **self.search_params)

        transients = get_transients_for_dataset(self.dataset.id)
        self.assertEqual(len(transients), 1)
        transient_properties = transients[0]
        self.assertEqual(transient_properties['transient_type'], 2)

        # Check that the bands for the images are the same as the transient's band
        freq_bands = self.dataset.frequency_bands()
        self.assertEqual(len(freq_bands), 1)
        self.assertEqual(freq_bands[0], transient_properties['band'])

        #Sanity check that the runcat is correctly matched
        runcats = self.dataset.runcat_entries()
        self.assertEqual(len(runcats), 1)
        self.assertEqual(runcats[0]['runcat'], transient_properties['runcat'])

        # Check that the trigger xtrsrc is linked to correct image (and hence
        # datetime).
        self.assertEqual(transient_properties['taustart_ts'],
                         im_params[-1]['taustart_ts'])


    def test_multi_epoch_source_flare_and_fade(self):
        """
        A steady source (i.e. detected in first image) flares up,
        then fades and finally disappears.
        """
        im_params = self.im_params
        transient_src = db_subs.MockSource(
             template_extractedsource=db_subs.example_extractedsource_tuple(
                 ra=im_params[0]['centre_ra'],
                 dec=im_params[0]['centre_decl'],
             ),
             lightcurve={
                 im_params[0]['taustart_ts'] : self.barely_detectable_flux,
                 im_params[1]['taustart_ts'] : 2*self.barely_detectable_flux,
                 im_params[2]['taustart_ts'] : self.barely_detectable_flux,
             }
        )

        inserted_sources = []

        for img_pars in im_params[:2]:
            image, blind_xtr,forced_fits = insert_image_and_simulated_sources(
                self.dataset,img_pars,[transient_src],
                self.new_source_sigma_margin)
            self.assertEqual(len(forced_fits), 0)
            inserted_sources.extend(blind_xtr)

        # Check the number of detected transients
        # This should be zero until we trigger a variability search,
        # since this source was detected in first image.
        transients = get_transients_for_dataset(self.dataset.id)
        self.assertEqual(len(transients), 0)

        #Trigger updating of variability indices
        transients = multi_epoch_transient_search(image_id=image.id,
                                          **self.search_params)

        transients = get_transients_for_dataset(self.dataset.id)
        self.assertEqual(len(transients), 1)

        transient_properties = transients[0]
        # Check that the bands for the images are the same as the transient's band
        freq_bands = self.dataset.frequency_bands()
        self.assertEqual(len(freq_bands), 1)
        self.assertEqual(freq_bands[0], transient_properties['band'])

        #Sanity check that the runcat is correctly matched
        runcats = self.dataset.runcat_entries()
        self.assertEqual(len(runcats), 1)
        self.assertEqual(runcats[0]['runcat'], transient_properties['runcat'])


        #'Variable' / multi-epoch transients have type 2:
        self.assertEqual(transient_properties['transient_type'],2)

        # Check that the trigger xtrsrc is linked to correct image (and hence
        # datetime).
        self.assertEqual(transient_properties['taustart_ts'],
                         transient_src.lightcurve.keys()[1])

        #Check we have sensible variability indices
        # print "\n",transient_properties
        metrics = db_subs.lightcurve_metrics(inserted_sources)
        # print "\nAfter two images:"
        for metric_name in 'v_int', 'eta_int':
            # print metric_name, transient_properties[metric_name]
            self.assertAlmostEqual(transient_properties[metric_name],
                             metrics[-1][metric_name])


        #Add 3rd image (another blind detection), check everything is sane
        image, blind_xtr,forced_fits = insert_image_and_simulated_sources(
            self.dataset,im_params[2],[transient_src],
            self.new_source_sigma_margin)
        self.assertEqual(len(forced_fits), 0)
        inserted_sources.extend(blind_xtr)
        transients = multi_epoch_transient_search(image_id=image.id,
                                      **self.search_params)

        # Check that the trigger xtrsrc is *still* linked to correct image
        transients = get_transients_for_dataset(self.dataset.id)
        self.assertEqual(len(transients), 1)
        transient_properties = transients[0]
        self.assertEqual(transient_properties['taustart_ts'],
                         transient_src.lightcurve.keys()[1])


        # Ok, now add the last image and check that we get a correct forced-fit
        # request:
        image, blind_xtr,forced_fits = insert_image_and_simulated_sources(
                self.dataset,im_params[3],[transient_src],
                self.new_source_sigma_margin)
        self.assertEqual(len(blind_xtr),0)
        self.assertEqual(len(forced_fits),1)
        inserted_sources.extend(forced_fits)

        # Trigger updating of variability indices
        transients = multi_epoch_transient_search(image_id=image.id,
                                          **self.search_params)

        # Variability indices should take non-detections into account
        transients = get_transients_for_dataset(self.dataset.id)
        self.assertEqual(len(transients), 1)
        transient_properties = transients[0]
        metrics = db_subs.lightcurve_metrics(inserted_sources)
        # print "\nAfter four images:"
        for metric_name in 'v_int', 'eta_int':
            # print metric_name, transient_properties[metric_name]
            self.assertAlmostEqual(transient_properties[metric_name],
                             metrics[-1][metric_name])



class TestDecreasingImageRMS(unittest.TestCase):
    """
    These unit-tests enumerate the possible cases where we process an image
    with a lower RMS value, and see a new source. Is it a transient, or
    just a steady source that was lost in the noise before?
    """
    def shortDescription(self):
         return None
    @requires_database()
    def setUp(self):
        self.database = tkp.db.Database()
        self.dataset = tkp.db.DataSet(
            data={'description':"Trans:" +self._testMethodName},
            database=self.database)

        self.n_images = 2
        self.rms_min_initial = 2e-3 #2mJy
        self.rms_max_initial = 5e-3 #5mJy
        self.new_src_sigma_margin = 3
        self.detection_thresh=10


        dt=self.detection_thresh
        margin = self.new_src_sigma_margin
        #These all refer to the first image, they should all be clearly
        #detected in the second image:
        self.barely_detectable_flux = 1.01*self.rms_min_initial*dt
        self.reliably_detected_at_image_centre_flux = (
                                        1.01*self.rms_min_initial*(dt+ margin))
        self.always_detectable_flux = 1.01*self.rms_max_initial*(dt+ margin)

        self.search_params = dict(eta_lim=1,
                                  V_lim=0.1,
                                  probability_threshold=0.7,
                                  minpoints=1, )


        test_specific_img_params = dict(rms_qc = self.rms_min_initial,
                                rms_min = self.rms_min_initial,
                                rms_max = self.rms_max_initial,
                                detection_thresh = self.detection_thresh)

        self.img_params = db_subs.generate_timespaced_dbimages_data(
            self.n_images, **test_specific_img_params)

        #Drop RMS to 1 mJy / 2.5mJy in second image.
        rms_decrease_factor = 0.5
        self.img_params[1]['rms_qc']*=rms_decrease_factor
        self.img_params[1]['rms_min']*=rms_decrease_factor
        self.img_params[1]['rms_max']*=rms_decrease_factor

    def tearDown(self):
        tkp.db.rollback()

    def test_certain_transient(self):
        """
        flux1 > (rms_max0*(det0+margin)
        --> Definite transient

        Nice and bright, must be new - mark it definite transient.
        """
        img_params = self.img_params

        bright_transient = MockSource(
            example_extractedsource_tuple(ra=img_params[0]['centre_ra'],
                                          dec=img_params[0]['centre_decl']),
            lightcurve={img_params[1]['taustart_ts']:
                            self.always_detectable_flux}
        )
        #First, check that we've set up the test correctly:
        rms_max0 = img_params[0]['rms_max']
        det0 = img_params[0]['detection_thresh']
        self.assertTrue(bright_transient.lightcurve.values()[0] >
            rms_max0*(det0 + self.new_src_sigma_margin ) )

        for pars in self.img_params:
            img = tkp.db.Image(data=pars,dataset=self.dataset)
            xtr = bright_transient.simulate_extraction(img,
                                                       extraction_type='blind')
            if xtr is not None:
                img.insert_extracted_sources([xtr],'blind')
            img.associate_extracted_sources(deRuiter_r, new_source_sigma_margin)
        transients = get_transients_for_dataset(self.dataset.id)

        #Should have one 'definite' transient
        self.assertEqual(len(transients),1)
        #With a 'transient_type' column
        self.assertTrue('transient_type' in transients[0])
        self.assertEqual(transients[0]['transient_type'], 1)

    def test_marginal_transient(self):
        """
        ( flux1 > (rms_min0*(det0 + margin) )
        but ( flux1 < (rms_max0*(det0 + margin) )
        --> Possible transient

        If it was in a region of rms_min, we would (almost certainly) have seen
        it in the first image. So new source --> Possible transient.
        But if it was in a region of rms_max, then perhaps we would have missed
        it. In which case, new source --> Just seeing deeper.

        Note that if we are tiling overlapping images, then the first time
        a field is processed with image-centre at the edge of the old field,
        we may get a bunch of unhelpful 'possible transients'.

        Furthermore, this will pick up fluctuating sources near the
        image-margins even with a fixed field of view.
        But without a more complex store of image-rms-per-position, we cannot
        do better.
        Hopefully we can use a 'distance from centre' feature to separate out
        the good and bad candidates in this case.
        """
        img_params = self.img_params

        #Must pick flux value carefully to fire correct logic branch:
        img0 = img_params[0]
        marginal_transient_flux = self.reliably_detected_at_image_centre_flux

        marginal_transient = MockSource(
            example_extractedsource_tuple(ra=img_params[0]['centre_ra'],
                                          dec=img_params[0]['centre_decl']),
            lightcurve={img_params[1]['taustart_ts'] : marginal_transient_flux}
        )


        #First, check that we've set up the test correctly:
        rms_min0 = img_params[0]['rms_min']
        rms_max0 = img_params[0]['rms_max']
        det0 = img_params[0]['detection_thresh']
        self.assertTrue(marginal_transient_flux <
            rms_max0*(det0 + self.new_src_sigma_margin ) )
        self.assertTrue(marginal_transient_flux >
            rms_min0*(det0 + self.new_src_sigma_margin ) )

        for pars in self.img_params:
            img = tkp.db.Image(data=pars,dataset=self.dataset)
            xtr = marginal_transient.simulate_extraction(img,
                                                       extraction_type='blind')
            if xtr is not None:
                img.insert_extracted_sources([xtr],'blind')
            img.associate_extracted_sources(deRuiter_r, new_source_sigma_margin)
        transients = get_transients_for_dataset(self.dataset.id)

        #Should have one 'possible' transient
        self.assertEqual(len(transients),1)
        #With a 'transient_type' column
        self.assertTrue('transient_type' in transients[0])
        self.assertEqual(transients[0]['transient_type'], 0)


    def test_probably_not_a_transient(self):
        """
        ( flux1 < (rms_min0*(det0 + margin) )
        --> Probably not a transient

        NB even if
            avg_source_flux == rms_min0*det0 + epsilon
        we might not detect it in the
        first image, due to noise fluctuations. So we provide the
        user-tunable marginal_detection_thresh, to ignore these 'noise'
        transients.
        """
        img_params = self.img_params

        img0 = img_params[0]
        marginal_steady_src_flux = self.barely_detectable_flux

        # This time around, we just manually exclude the steady src from
        # the first image detections.

        marginal_steady_src = MockSource(
            example_extractedsource_tuple(ra=img_params[0]['centre_ra'],
                                          dec=img_params[0]['centre_decl']
                                          ),
            lightcurve=defaultdict(lambda :marginal_steady_src_flux)
        )

        #First, check that we've set up the test correctly:
        rms_min0 = img_params[0]['rms_min']
        det0 = img_params[0]['detection_thresh']
        self.assertTrue(marginal_steady_src_flux <
            rms_min0*(det0 + self.new_src_sigma_margin ) )

        #Insert first image, no sources.
        tkp.db.Image(data=img_params[0],dataset=self.dataset)
        #Now set up second image.
        img1 = tkp.db.Image(data=img_params[1],dataset=self.dataset)
        xtr = marginal_steady_src.simulate_extraction(img1,
                                                    extraction_type='blind')
        img1.insert_extracted_sources([xtr],'blind')
        img1.associate_extracted_sources(deRuiter_r, new_source_sigma_margin)
        transients = get_transients_for_dataset(self.dataset.id)

        #Should have no marked transients
        self.assertEqual(len(transients),0)


class TestIncreasingImageRMS(unittest.TestCase):
    def shortDescription(self):
         return None
    @requires_database()
    def setUp(self):
        self.database = tkp.db.Database()
        self.dataset = tkp.db.DataSet(
            data={'description':"Trans:" +self._testMethodName},
            database=self.database)

        self.n_images = 2
        self.rms_min_initial = 2e-3 #2mJy
        self.rms_max_initial = 5e-3 #5mJy
        self.new_source_sigma_margin = 3
        self.detection_thresh=10

        dt=self.detection_thresh
        self.barely_detectable_flux = 1.01*dt*self.rms_min_initial

        test_specific_img_params = dict(rms_qc = self.rms_min_initial,
                                rms_min = self.rms_min_initial,
                                rms_max = self.rms_max_initial,
                                detection_thresh = self.detection_thresh)

        self.img_params = db_subs.generate_timespaced_dbimages_data(
            self.n_images, **test_specific_img_params)

        #Increase RMS to 4 mJy / 10mJy in second image.
        rms_increase_factor = 2.0
        self.img_params[1]['rms_qc']*=rms_increase_factor
        self.img_params[1]['rms_min']*=rms_increase_factor
        self.img_params[1]['rms_max']*=rms_increase_factor

        self.search_params = dict(eta_lim=1,
                          V_lim=0.1,
                          probability_threshold=0.7,
                          minpoints=1, )

    def tearDown(self):
        tkp.db.rollback()

    def test_null_detection_business_as_usual(self):
        """
        If we do not blindly extract a steady source due to increased RMS,
        then we expect a null-detection forced-fit to be triggered.

        However, if the source properties are steady, this should not
        result in the source being identified as transient.
        """

        img0 = self.img_params[0]
        steady_src_flux = self.barely_detectable_flux
        steady_src = MockSource(
            example_extractedsource_tuple(ra=img0['centre_ra'],
                                          dec=img0['centre_decl']
                                          ),
            lightcurve=defaultdict(lambda :steady_src_flux)
        )


        image, blind_xtr,forced_fits = insert_image_and_simulated_sources(
                self.dataset,self.img_params[0],[steady_src],
                self.new_source_sigma_margin)
        self.assertEqual(len(blind_xtr),1)
        self.assertEqual(len(forced_fits),0)

        image, blind_xtr,forced_fits = insert_image_and_simulated_sources(
                self.dataset,self.img_params[1],[steady_src],
                self.new_source_sigma_margin)
        self.assertEqual(len(blind_xtr),0)
        self.assertEqual(len(forced_fits),1)
        multi_epoch_transient_search(image_id=image.id,
                                    **self.search_params)

        transients=get_transients_for_dataset(self.dataset.id)
        self.assertEqual(len(transients),0)



class TestMultipleFrequencyBands(unittest.TestCase):
    """
    We expect to see some steady sources in only one frequency band,
    due to steep spectral indices. We don't want to misclassify these as
    transient without any proof of variability!
    """
    def shortDescription(self):
         return None
    @requires_database()
    def setUp(self):
        self.database = tkp.db.Database()
        self.dataset = tkp.db.DataSet(
            data={'description':"Trans:" +self._testMethodName},
            database=self.database)

        self.n_images = 2
        self.rms_min = 1e-3 #1mJy
        self.rms_max = 2e-3 #2mJy
        self.new_src_sigma_margin = 3
        self.detection_thresh=10

        self.first_image_freq = 250e6 # 250 MHz
        self.second_image_freq = 50e6 # 50 MHz


        dt=self.detection_thresh
        margin = self.new_src_sigma_margin
        self.always_detectable_flux = 1.01*self.rms_max*(dt+ margin)

        self.search_params = dict(eta_lim=1,
                                  V_lim=0.1,
                                  probability_threshold=0.7,
                                  minpoints=1, )

        test_specific_img_params = dict(
            freq_eff = self.first_image_freq,
            rms_qc = self.rms_min,
            rms_min = self.rms_min,
            rms_max = self.rms_max,
            detection_thresh = self.detection_thresh)

        self.img_params = db_subs.generate_timespaced_dbimages_data(
            self.n_images, **test_specific_img_params)

        self.img_params[1]['freq_eff']=self.second_image_freq


    def tearDown(self):
        tkp.db.rollback()

    def test_probably_not_a_transient(self):
        """
        No source at 250MHz, but we detect a source at 50MHz.
        Not necessarily a transient.
        Should trivially ignore 250MHz data when looking at a new 50MHz source.
        """
        img_params = self.img_params

        img0 = img_params[0]

        # This time around, we just manually exclude the steady src from
        # the first image detections.
        steady_low_freq_src = MockSource(
            example_extractedsource_tuple(ra=img_params[0]['centre_ra'],
                                          dec=img_params[0]['centre_decl']
                                          ),
            lightcurve=defaultdict(lambda :self.always_detectable_flux)
        )

        #Insert first image, no sources.
        tkp.db.Image(data=img_params[0],dataset=self.dataset)
        #Now set up second image.
        img1 = tkp.db.Image(data=img_params[1],dataset=self.dataset)
        xtr = steady_low_freq_src.simulate_extraction(img1,
                                                    extraction_type='blind')
        img1.insert_extracted_sources([xtr],'blind')
        img1.associate_extracted_sources(deRuiter_r, new_source_sigma_margin)
        transients = get_transients_for_dataset(self.dataset.id)

        #Should have no marked transients
        self.assertEqual(len(transients),0)


class TestMultipleSourceField(unittest.TestCase):
    """
    By testing a field with multiple sources, we at least go some way
    to ensuring there is no misclassification in the SQL queries
    when we have multiple transient candidates in play.
    """
    @requires_database()
    def setUp(self):
        self.database = tkp.db.Database()
        self.dataset = tkp.db.DataSet(
            data={'description':"Trans:" +self._testMethodName},
            database=self.database)

        self.n_images = 8
        self.image_rms = 1e-3 # 1mJy
        self.new_source_sigma_margin = 3
        self.search_params = dict(eta_lim=1,
                                  V_lim=0.1,
                                  probability_threshold=0.7,
                                  minpoints=1, )
        detection_thresh=10

        barely_detectable_flux = 1.01*self.image_rms*(detection_thresh)
        reliably_detectable_flux = (
            1.01*self.image_rms*(detection_thresh+self.new_source_sigma_margin))

        test_specific_img_params = dict(rms_qc =self.image_rms,
                                        rms_min = self.image_rms,
                                        rms_max = self.image_rms,
                                        detection_thresh = detection_thresh)

        self.img_params = db_subs.generate_timespaced_dbimages_data(
            self.n_images, **test_specific_img_params)
        imgs=self.img_params
        first_img = imgs[0]
        centre_ra = first_img['centre_ra']
        centre_decl = first_img['centre_decl']
        xtr_radius = first_img['xtr_radius']


        #At centre
        fixed_source = MockSource(
            example_extractedsource_tuple(ra=centre_ra, dec=centre_decl),
            lightcurve=defaultdict(lambda: barely_detectable_flux))

        #How many transients should we know about after each image?
        self.n_transients_after_image = defaultdict(lambda:0)
        self.n_transient_types = defaultdict(lambda:0)

        #Should be immediately flagged as type-0 (almost certain) transient
        #shifted to +ve RA
        bright_fast_transient = MockSource(
            example_extractedsource_tuple(ra=centre_ra + xtr_radius * 0.5,
                                          dec=centre_decl),
            lightcurve={imgs[3]['taustart_ts']: reliably_detectable_flux}
        )
        #Detect immediately
        for img_idx in range(3,self.n_images):
            self.n_transients_after_image[img_idx]+=1
        #Type 0
        self.n_transient_types[1]+=1

        # Should not be flagged as transient until forced-fit in image[4]
        # shows high-variance
        # shifted to -ve RA
        weak_fast_transient = MockSource(
            example_extractedsource_tuple(ra=centre_ra - xtr_radius * 0.5,
                                          dec=centre_decl),
            lightcurve={imgs[3]['taustart_ts']: barely_detectable_flux}
        )
        #Detect after one forced-fit in image 4
        for img_idx in range(4,self.n_images):
            self.n_transients_after_image[img_idx]+=1
        #Type 2
        self.n_transient_types[2]+=1

        # shifted to +ve Dec
        # Should not be flagged as transient until forced-fit in image[7]
        # shows high-variance
        weak_slow_transient = MockSource(
            example_extractedsource_tuple(ra=centre_ra,
                                          dec=centre_decl + xtr_radius * 0.5),
            lightcurve={imgs[5]['taustart_ts']: barely_detectable_flux,
                        imgs[6]['taustart_ts']: barely_detectable_flux*0.95}
        )
        #Detect after sudden drop in forced-fit value, image 7
        for img_idx in range(7,self.n_images):
            self.n_transients_after_image[img_idx]+=1
        #Type 2
        self.n_transient_types[2]+=1

        self.all_mock_sources = [fixed_source, weak_slow_transient,
                                 bright_fast_transient, weak_fast_transient]


    def tearDown(self):
        tkp.db.rollback()


    def test_full_transient_search_routine(self):
        inserted_imgs = []
        for img_idx in xrange(self.n_images):
            image, _,_ = insert_image_and_simulated_sources(
                self.dataset,self.img_params[img_idx],self.all_mock_sources,
                self.new_source_sigma_margin)
            inserted_imgs.append(image)
            transients = multi_epoch_transient_search(image_id=image.id,
                                  **self.search_params)
            discovered_transients = get_transients_for_dataset(self.dataset.id)
            self.assertEqual(len(discovered_transients),
                             self.n_transients_after_image[img_idx])

        #Sanity check that everything went into one band
        bands = self.dataset.frequency_bands()
        self.assertEqual(len(bands), 1)

        all_transients = get_transients_for_dataset(self.dataset.id)

        transient_type_results = [t['transient_type'] for t in all_transients]
        for type_num in self.n_transient_types:
            self.assertEqual(transient_type_results.count(type_num),
                             self.n_transient_types[type_num])

#        for t in all_transients:
#            print "V_int:", t['v_int'], "  eta_int:", t['eta_int']
        #Now test thresholding:
        more_highly_variable = sum(t['v_int'] > 2.0 for t in all_transients)
        very_non_flat = sum(t['eta_int'] > 100.0 for t in all_transients)

        high_v_transients = multi_epoch_transient_search(
                 eta_lim=1.1,
                 V_lim=2.0,
                 probability_threshold=0.01,
                 image_id=inserted_imgs[-1].id,
                 minpoints=1)
        self.assertEqual(len(high_v_transients), more_highly_variable)

        high_eta_transients = multi_epoch_transient_search(
                 eta_lim=100,
                 V_lim=0.01,
                 probability_threshold=0.01,
                 image_id=inserted_imgs[-1].id,
                 minpoints=1)
        self.assertEqual(len(high_eta_transients), very_non_flat)



class TestIssue4306(unittest.TestCase):
    """
    Check that the database schema rejects a transient with null-valued
    variability indices
    """

    @requires_database()
    def setUp(self):
        self.database = tkp.db.Database()

    def tearDown(self):
        tkp.db.rollback()

    def test_variability_not_null(self):
            # As per #4306, it should be impossible to insert a transient with a
            # null value for V_int or eta_int.

            # To satisfy foreign key constraints, we need to use a matching
            # runningcatalog and extractedsource entry.
            cursor = self.database.connection.cursor()
            cursor.execute("SELECT id, xtrsrc from runningcatalog LIMIT 1")
            rc, xtrsrc = cursor.fetchone()

            transients = [
                {'runcat': rc,
                 'band': 0,
                 'siglevel': 0,
                 'v_int': None,
                 'eta_int': None,
                 'trigger_xtrsrc': xtrsrc}
            ]
            # MonetDB raises OperationalError; Postgres raises IntegrityError.
            # (IntegrityError is correct per PEP 249.)
            possible_errors = (
                self.database.exceptions.OperationalError,
                self.database.exceptions.IntegrityError
            )
            with self.assertRaises(possible_errors):
                _insert_variable_source_transients(transients)
