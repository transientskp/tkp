import unittest
from collections import defaultdict
import tkp.db
from tkp.db.transients import multi_epoch_transient_search
from tkp.db.transients import _insert_transients
from tkp.db.generic import get_db_rows_as_dicts
from tkp.db import nulldetections
from tkp.testutil import db_subs
from tkp.testutil.db_subs import (MockSource,
                                  example_extractedsource_tuple,
                                  get_transients_for_dataset)

from tkp.testutil.decorators import requires_database


class TestSimplestCases(unittest.TestCase):
    """
    Various basic test-cases of the transient-detection logic.

    In these simple cases we just have one source, and fixed image properties.
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
        # 1mJy image RMS, 10-sigma detection threshold = 10mJy threshold.
        test_specific_img_params = dict(rms_qc = image_rms,
                                rms_min = image_rms,
                                rms_max = image_rms,
                                detection_thresh = 10)

        self.im_params = db_subs.generate_timespaced_dbimages_data(
            self.n_images,**test_specific_img_params)

    def tearDown(self):
        tkp.db.rollback()

    def test_single_epoch_bright_transient(self):
        """A bright transient appears at field centre in one image."""
        im_params = self.im_params
        transient_src = db_subs.MockSource(
             template_extractedsource=db_subs.example_extractedsource_tuple(
                 ra=im_params[0]['centre_ra'],
                 dec=im_params[0]['centre_decl'],
             ),
             lightcurve={im_params[2]['taustart_ts'] : 200e-3}
        )

        for img_pars in im_params[:3]:
            image = tkp.db.Image(dataset=self.dataset, data=img_pars)
            blind_extraction = transient_src.simulate_extraction(
                image, extraction_type='blind')
            if blind_extraction is not None:
                image.insert_extracted_sources([blind_extraction], 'blind')
            image.associate_extracted_sources(deRuiter_r=3.7,
                new_source_sigma_margin=self.new_source_sigma_margin)
            #Sanity check - we do not expect any nulldetections requested yet
            nd_posns = nulldetections.get_nulldetections(image.id)
            self.assertEqual(nd_posns, [])

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

        # Check that the trigger xtrsrc is linked to correct image (and hence
        # datetime).
        query = """\
        select taustart_ts
          from extractedsource x
              ,image i
         where x.image = i.id
           and x.id = (select trigger_xtrsrc
                         from transient t
                             ,runningcatalog r
                        where t.runcat = r.id
                          and r.dataset = %s
                      )
        """
        self.database.cursor.execute(query, (self.dataset.id,))
        trigger_times = get_db_rows_as_dicts(self.database.cursor)
        self.assertEqual(len(trigger_times), 1)
        ts = trigger_times[0]['taustart_ts']
        self.assertEqual(ts, transient_src.lightcurve.keys()[0])

        # Ok, now add the last image and check that we get a correct forced-fit
        # request:
        image = tkp.db.Image(dataset=self.dataset, data=im_params[3])
        image.associate_extracted_sources(deRuiter_r=3.7,
                new_source_sigma_margin=self.new_source_sigma_margin)
        nd_posns = nulldetections.get_nulldetections(image.id)
        self.assertEqual(len(nd_posns),1)
        self.assertEqual(nd_posns[0][0],transient_src.base_source.ra)
        self.assertEqual(nd_posns[0][1],transient_src.base_source.dec)
        image.insert_extracted_sources(
            [transient_src.simulate_extraction(image, extraction_type='ff_nd')],
            'ff_nd')
        nulldetections.associate_nd(image.id)

        #Trigger updating of variability indices
        transients = multi_epoch_transient_search(
                                eta_lim=1,
                                V_lim=0.1,
                                probability_threshold=0.7,
                                minpoints=1,
                                image_id=image.id)

        #And now we should have a non-zero variability value:
        transients = get_transients_for_dataset(self.dataset.id)
        self.assertEqual(len(transients), 1)
        transient_properties = transients[0]
        # print "\n",transient_properties
        self.assertNotAlmostEqual(transient_properties['v_int'],0)
        self.assertNotAlmostEqual(transient_properties['eta_int'],0)

    def test_multi_epoch_source_flare_and_fade(self):
        """
        A steady source (i.e. detected in first image) flares up,
        then disappears.
        """
        im_params = self.im_params
        transient_src = db_subs.MockSource(
             template_extractedsource=db_subs.example_extractedsource_tuple(
                 ra=im_params[0]['centre_ra'],
                 dec=im_params[0]['centre_decl'],
             ),
             lightcurve={
                 im_params[0]['taustart_ts'] : 15e-3,
                 im_params[1]['taustart_ts'] : 30e-3,
                 im_params[2]['taustart_ts'] : 15e-3,
             }
        )

        inserted_sources = []

        for img_pars in im_params[:2]:
            image = tkp.db.Image(dataset=self.dataset, data=img_pars)
            blind_extraction = transient_src.simulate_extraction(
                image, extraction_type='blind')
            if blind_extraction is not None:
                image.insert_extracted_sources([blind_extraction], 'blind')
            inserted_sources.append(blind_extraction)
            image.associate_extracted_sources(deRuiter_r=3.7,
                new_source_sigma_margin=self.new_source_sigma_margin)
            #Sanity check - we do not expect any nulldetections requested yet
            nd_posns = nulldetections.get_nulldetections(image.id)
            self.assertEqual(nd_posns, [])

        # Check the number of detected transients
        # This should be zero until we trigger a variability search,
        # since this source was detected in first image.
        transients = get_transients_for_dataset(self.dataset.id)
        self.assertEqual(len(transients), 0)

        #Trigger updating of variability indices
        transients = multi_epoch_transient_search(
                                eta_lim=1,
                                V_lim=0.1,
                                probability_threshold=0.7,
                                minpoints=1,
                                image_id=image.id)

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


        # Check that the trigger xtrsrc is linked to correct image (and hence
        # datetime).
        transient_trigger_times_query = """\
        select taustart_ts
          from extractedsource x
              ,image i
         where x.image = i.id
           and x.id = (select trigger_xtrsrc
                         from transient t
                             ,runningcatalog r
                        where t.runcat = r.id
                          and r.dataset = %s
                      )
        """
        self.database.cursor.execute(transient_trigger_times_query,
                                     (self.dataset.id,))
        trigger_times = get_db_rows_as_dicts(self.database.cursor)
        self.assertEqual(len(trigger_times), 1)
        ts = trigger_times[0]['taustart_ts']
        self.assertEqual(ts, transient_src.lightcurve.keys()[1])

        #Check we have sensible variability indices
        # print "\n",transient_properties
        metrics = db_subs.lightcurve_metrics(inserted_sources)
        # print "\nAfter two images:"
        for metric_name in 'v_int', 'eta_int':
            # print metric_name, transient_properties[metric_name]
            self.assertAlmostEqual(transient_properties[metric_name],
                             metrics[-1][metric_name])


        #Add 3rd image (another blind detection), check everything is sane
        for img_pars in [im_params[2]]:
            image = tkp.db.Image(dataset=self.dataset, data=img_pars)
            blind_extraction = transient_src.simulate_extraction(
                image, extraction_type='blind')
            if blind_extraction is not None:
                image.insert_extracted_sources([blind_extraction], 'blind')
                inserted_sources.append(blind_extraction)
            image.associate_extracted_sources(deRuiter_r=3.7,
                new_source_sigma_margin=self.new_source_sigma_margin)
            #Sanity check - we do not expect any nulldetections requested yet
            nd_posns = nulldetections.get_nulldetections(image.id)
            self.assertEqual(nd_posns, [])
            transients = multi_epoch_transient_search(
                                eta_lim=1,
                                V_lim=0.1,
                                probability_threshold=0.7,
                                minpoints=1,
                                image_id=image.id)


        # Check that the trigger xtrsrc is *still* linked to correct image
        self.database.cursor.execute(transient_trigger_times_query,
                                     (self.dataset.id,))
        trigger_times = get_db_rows_as_dicts(self.database.cursor)
        self.assertEqual(len(trigger_times), 1)
        ts = trigger_times[0]['taustart_ts']
        self.assertEqual(ts, transient_src.lightcurve.keys()[1])


        # Ok, now add the last image and check that we get a correct forced-fit
        # request:
        image = tkp.db.Image(dataset=self.dataset, data=im_params[3])
        image.associate_extracted_sources(deRuiter_r=3.7,
                new_source_sigma_margin=self.new_source_sigma_margin)
        nd_posns = nulldetections.get_nulldetections(image.id)
        self.assertEqual(len(nd_posns),1)
        self.assertEqual(nd_posns[0][0],transient_src.base_source.ra)
        self.assertEqual(nd_posns[0][1],transient_src.base_source.dec)
        forced_fit = transient_src.simulate_extraction(image,
                                                       extraction_type='ff_nd')
        image.insert_extracted_sources([forced_fit], 'ff_nd')
        inserted_sources.append(forced_fit)
        nulldetections.associate_nd(image.id)

        # Trigger updating of variability indices
        transients = multi_epoch_transient_search(
                                eta_lim=1,
                                V_lim=0.1,
                                probability_threshold=0.7,
                                minpoints=1,
                                image_id=image.id)

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


class TestMultipleSourceField(unittest.TestCase):
    @requires_database()
    def setUp(self):
        self.database = tkp.db.Database()
        self.dataset = tkp.db.DataSet(
            data={'description':"Trans:" +self._testMethodName},
            database=self.database)

        self.n_images = 8
        self.image_rms = 1e-3 # 1mJy
        self.new_source_sigma_margin = 3

        test_specific_img_params = dict(rms_qc =self.image_rms,
                                        rms_min = self.image_rms,
                                        rms_max = self.image_rms,
                                        detection_thresh = 10)

        self.img_params = db_subs.generate_timespaced_dbimages_data(
            self.n_images, **test_specific_img_params)

        first_img = self.img_params[0]
        centre_ra = first_img['centre_ra']
        centre_decl = first_img['centre_decl']
        xtr_radius = first_img['xtr_radius']

        # OK, here's the fiddly part:
        # we want to generate per-image source lists representing a bunch of
        # transient sources.
        # Note that we must ensure they all lie within the image-extraction
        # regions, to keep things realistic.

        # Mock sources are as follows:
        #     1 Fixed source, present in all lists returned.
        #     2 `fast transients`
        #         1 present in images[3], 30 mJy
        #         1 present in images[4], 5 mJy
        #     1 `slow transient`,
        #         present in images indices [5]  (4mJy) and [6], (3mJy)

        #At centre
        fixed_source = MockSource(
            example_extractedsource_tuple(ra=centre_ra, dec=centre_decl),
            lightcurve=defaultdict(lambda: 15e-3))

        imgs = self.img_params
        #shifted to +ve RA
        bright_fast_transient = MockSource(
            example_extractedsource_tuple(ra=centre_ra + xtr_radius * 0.5,
                                          dec=centre_decl),
            lightcurve={imgs[3]['taustart_ts']: 30e-3}
        )

        # shifted to -ve RA
        weak_fast_transient = MockSource(
            example_extractedsource_tuple(ra=centre_ra - xtr_radius * 0.5,
                                          dec=centre_decl),
            lightcurve={imgs[4]['taustart_ts']: 11e-3}
        )

        # shifted to +ve Dec
        weak_slow_transient = MockSource(
            example_extractedsource_tuple(ra=centre_ra,
                                          dec=centre_decl + xtr_radius * 0.5),
            lightcurve={imgs[5]['taustart_ts']: 11e-3,
                        imgs[6]['taustart_ts']: 5e-3}
        )

        self.all_mock_sources = [fixed_source, weak_slow_transient,
                                 bright_fast_transient, weak_fast_transient]
        self.n_expected_transients = 3


    def tearDown(self):
        tkp.db.rollback()


    def test_full_transient_search_routine(self):
        self.db_imgs = []
        for i in xrange(self.n_images):
            img = tkp.db.Image(data=self.img_params[i],dataset=self.dataset)
            self.db_imgs.append(img)
            blind_extractions=[]
            for src in self.all_mock_sources:
                xtr = src.simulate_extraction(img,extraction_type='blind')
                if xtr is not None:
                    blind_extractions.append(xtr)
            self.db_imgs[i].insert_extracted_sources(blind_extractions,'blind')
            self.db_imgs[i].associate_extracted_sources(deRuiter_r=3.7,
                new_source_sigma_margin=self.new_source_sigma_margin)

        #Sanity check that everything went into one band
        bands = self.dataset.frequency_bands()
        self.assertEqual(len(bands), 1)

        #First run with lax limits:
        variability_transients = multi_epoch_transient_search(
                                 eta_lim=1.1,
                                 V_lim=0.01,
                                 probability_threshold=0.01,
                                 image_id=self.db_imgs[-1].id,
                                 minpoints=1)


        all_transients = get_transients_for_dataset(self.dataset.id)
        self.assertEqual(len(all_transients),
                         self.n_expected_transients)
#        for t in all_transients:
#            print "V_int:", t['v_int'], "  eta_int:", t['eta_int']
        #Now test thresholding:
        more_highly_variable = sum(t['v_int'] > 2.0 for t in all_transients)
        very_non_flat = sum(t['eta_int'] > 100.0 for t in all_transients)

        transients = multi_epoch_transient_search(
                 eta_lim=1.1,
                 V_lim=2.0,
                 probability_threshold=0.01,
                 image_id=self.db_imgs[-1].id,
                 minpoints=1)
        self.assertEqual(len(transients), more_highly_variable)

        transients = multi_epoch_transient_search(
                 eta_lim=100,
                 V_lim=0.01,
                 probability_threshold=0.01,
                 image_id=self.db_imgs[-1].id,
                 minpoints=1)
        self.assertEqual(len(transients), very_non_flat)


class TestDecreasingImageRMS(unittest.TestCase):
    """
    These unit-tests flesh out the possible cases where we process an image
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
        # det_thresh==10 =>
        # Certain detection requires flux > (50mJy + margin of error)
        test_specific_img_params = dict(rms_qc = self.rms_min_initial,
                                rms_min = self.rms_min_initial,
                                rms_max = self.rms_max_initial,
                                detection_thresh = 10)

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
            lightcurve={img_params[1]['taustart_ts']: 100e-3}
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
            img.associate_extracted_sources(deRuiter_r=3.7)
        transients = get_transients_for_dataset(self.dataset.id)

        #Should have one 'definite' transient
        self.assertEqual(len(transients),1)
        #With a 'type' column
        self.assertTrue('type' in transients[0])
        # so 0=> Certain, 1=> Maybe?
        self.assertEqual(transients[0]['type'], 0)

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
        marginal_transient_flux = (img0['rms_min']*
               (img0['detection_thresh'] + self.new_src_sigma_margin + 0.5))

        marginal_transient = MockSource(
            example_extractedsource_tuple(ra=img_params[0]['centre_ra'],
                                          dec=img_params[0]['centre_decl']),
            lightcurve={img_params[1]['taustart_ts']: marginal_transient_flux}
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
            img.associate_extracted_sources(deRuiter_r=3.7)
        transients = get_transients_for_dataset(self.dataset.id)

        #Should have one 'possible' transient
        self.assertEqual(len(transients),1)
        #With a 'type' column
        self.assertTrue('type' in transients[0])
        # Set to a significant value. so 0=> Certain, 1=> Maybe?
        self.assertEqual(transients[0]['type'], 1)


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
        marginal_steady_src_flux = (img0['rms_min']*
                                (img0['detection_thresh'] + 0.001))

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
        img1.associate_extracted_sources(deRuiter_r=3.7)
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
        self.new_src_sigma_margin= 3
        # det_thresh==10 =>
        # Certain detection requires flux > (50mJy + margin of error)
        test_specific_img_params = dict(rms_qc = self.rms_min_initial,
                                rms_min = self.rms_min_initial,
                                rms_max = self.rms_max_initial,
                                detection_thresh = 10)

        self.img_params = db_subs.generate_timespaced_dbimages_data(
            self.n_images, **test_specific_img_params)

        #Increase RMS to 4 mJy / 10mJy in second image.
        rms_increase_factor = 2.0
        self.img_params[1]['rms_qc']*=rms_increase_factor
        self.img_params[1]['rms_min']*=rms_increase_factor
        self.img_params[1]['rms_max']*=rms_increase_factor


    def tearDown(self):
        tkp.db.rollback()

    def test_null_detection_business_as_usual(self):
        """
        If we do not blindly extract a steady source due to increased RMS,
        then we expect a null-detection forced-fit to be triggered.
        """
        img_pars = self.img_params

        img0 = img_pars[0]
        steady_src_flux = (img0['rms_min']* (img0['detection_thresh'] + 0.001))
        steady_src = MockSource(
            example_extractedsource_tuple(ra=img_pars[0]['centre_ra'],
                                          dec=img_pars[0]['centre_decl']
                                          ),
            lightcurve=defaultdict(lambda :steady_src_flux)
        )

        #Insert first image
        img0= tkp.db.Image(data=img_pars[0],dataset=self.dataset)
        xtr = steady_src.simulate_extraction(img0,extraction_type='blind')
        #Check MockSource working correctly and parameters all set right:
        self.assertIsNotNone(xtr)
        img0.insert_extracted_sources([xtr],'blind')
        img0.associate_extracted_sources(deRuiter_r=3.7,
                 new_source_sigma_margin=self.new_src_sigma_margin)
        #Now set up second image.
        img1 = tkp.db.Image(data=img_pars[1],dataset=self.dataset)
        xtr = steady_src.simulate_extraction(img1, extraction_type='blind')

        #Check MockSource working correctly and parameters all set right:
        self.assertIsNone(xtr) #So no insertion / association to do.

        #Check we still get a null-detection request
        # (This should be simple logic - no-detection, and in-field? Then
        # trigger a forced-fit. But it's still worth unit-testing.)
        nd_posns = nulldetections.get_nulldetections(img1.id)
        self.assertEqual(len(nd_posns),1)
        self.assertEqual(nd_posns[0][0],steady_src.base_source.ra)
        self.assertEqual(nd_posns[0][1],steady_src.base_source.dec)




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
                _insert_transients(transients)
