import unittest
import logging
    
import tkp.database as tkpdb
from .. import db_subs
from ..decorators import requires_database
import tkp.database.utils as db_utils

class TestSourceAssociation(unittest.TestCase):
    @requires_database()
    def setUp(self):
    
        self.database = tkpdb.DataBase()
#        Often fixes things if the database is playing up:
        db_subs.delete_test_database(self.database)
        self.dataset = tkpdb.DataSet(data={'description':"Src. assoc:"+self._testMethodName},
                                                    database = self.database)
        
        self.im_params = db_subs.example_dbimage_datasets(n_images=8)
        self.db_imgs=[]

    def tearDown(self):
        """remove all stuff after the test has been run"""
        self.database.connection.rollback()
        self.database.execute("delete from assocxtrsource")
        self.database.execute("delete from runningcatalog_flux")
        self.database.execute("delete from runningcatalog")
        self.database.close()

        
    def test_null_case_sequential(self):
        for im in self.im_params:
            self.db_imgs.append( tkpdb.dataset.Image( data=im, dataset=self.dataset) )
            self.db_imgs[-1].associate_extracted_sources()
            running_cat = tkpdb.utils.columns_from_table(self.database.connection,
                                           table="runningcatalog",
                                           keywords="*",
                                           where={"dataset":self.dataset.id})
            self.assertEqual(len(running_cat), 0)
            
#    def test_null_case_post_insert(self):
#        for im in self.im_params:
#            self.db_imgs.append( tkpdb.dataset.Image( data=im, dataset=self.dataset) )            
#        pass
    
    def test_only_first_epoch_source(self):
        """test_only_first_epoch_source
        
        - Pretend to extract a source only from the first image.
        - Run source association for each image, as we would in Trap.
        - Check the image source listing works
        - Check runcat and assocxtrsource are correct.
        
        """
            
            
        first_epoch = True
        extracted_source_ids=[]
        for im in self.im_params:
            self.db_imgs.append( tkpdb.dataset.Image( data=im, dataset=self.dataset) )
            last_img =self.db_imgs[-1] 
            
            if first_epoch:
                last_img.insert_extracted_sources([db_subs.example_extractedsource_tuple()])
                
            last_img.associate_extracted_sources()
            
            #First, check the runcat has been updated correctly:
            running_cat = tkpdb.utils.columns_from_table(self.database.connection,
                                           table="runningcatalog",
                                           keywords=['datapoints'],
                                           where={"dataset":self.dataset.id})
            self.assertEqual(len(running_cat), 1)
            self.assertEqual(running_cat[0]['datapoints'], 1)
            
            last_img.update()
            last_img.update_sources()
            img_xtrsrc_ids = [src.id for src in last_img.sources]
#            print "ImageID:", last_img.id
#            print "Imgs sources:", img_xtrsrc_ids
            if first_epoch:
                self.assertEqual(len(img_xtrsrc_ids),1)
                extracted_source_ids.extend(img_xtrsrc_ids)
                assocxtrsrcs_rows = tkpdb.utils.columns_from_table(self.database.connection,
                                           table="assocxtrsource",
                                           keywords=['runcat', 'xtrsrc' ],
                                           where={"xtrsrc":img_xtrsrc_ids[0]})
                self.assertEqual(len(assocxtrsrcs_rows),1)
                self.assertEqual(assocxtrsrcs_rows[0]['xtrsrc'], img_xtrsrc_ids[0])
            else:
                self.assertEqual(len(img_xtrsrc_ids),0)
            
            first_epoch=False
            
        
        #Assocxtrsources still ok after multiple images?
        self.assertEqual(len(extracted_source_ids),1)
        assocxtrsrcs_rows = tkpdb.utils.columns_from_table(self.database.connection,
                                           table="assocxtrsource",
                                           keywords=['runcat', 'xtrsrc' ],
                                           where={"xtrsrc":extracted_source_ids[0]})
        self.assertEqual(len(assocxtrsrcs_rows),1)
        
        self.assertEqual(assocxtrsrcs_rows[0]['xtrsrc'], extracted_source_ids[0],
                         "Runcat xtrsrc entry must match the only extracted source")
            

    def test_single_fixed_source(self):
        """test_single_fixed_source
        
        - Pretend to extract the same source in each of a series of images.
        - Perform source association 
        - Check the image source listing works
        - Check runcat, assocxtrsource.
        """
        
        imgs_loaded = 0
        first_image = True
        fixed_src_runcat_id = None
        for im in self.im_params:
            self.db_imgs.append( tkpdb.dataset.Image( data=im, dataset=self.dataset) )
            last_img =self.db_imgs[-1]
            last_img.insert_extracted_sources([db_subs.example_extractedsource_tuple()])
            last_img.associate_extracted_sources()
            imgs_loaded+=1
            running_cat = tkpdb.utils.columns_from_table(self.database.connection,
                                           table="runningcatalog",
                                           keywords=['id', 'datapoints'],
                                           where={"dataset":self.dataset.id})
            self.assertEqual(len(running_cat), 1)
            self.assertEqual(running_cat[0]['datapoints'], imgs_loaded)
            if first_image:
                fixed_src_runcat_id = running_cat[0]['id']
                self.assertIsNotNone(fixed_src_runcat_id, "No runcat id assigned to source")
            self.assertEqual(running_cat[0]['id'], fixed_src_runcat_id,
                             "Multiple runcat ids for same fixed source")
                           
            last_img.update()
            last_img.update_sources()
            img_xtrsrc_ids = [src.id for src in last_img.sources]
            self.assertEqual(len(img_xtrsrc_ids), 1)

            #Get the association row for most recent extraction:
            assocxtrsrcs_rows = tkpdb.utils.columns_from_table(self.database.connection,
                                       table="assocxtrsource",
                                       keywords=['runcat', 'xtrsrc' ],
                                       where={"xtrsrc":img_xtrsrc_ids[0]})
#            print "ImageID:", last_img.id
#            print "Imgs sources:", img_xtrsrc_ids
#            print "Assoc entries:", assocxtrsrcs_rows 
#            print "First extracted source id:", ds_source_ids[0]
#            if len(assocxtrsrcs_rows):
#                print "Associated source:", assocxtrsrcs_rows[0]['xtrsrc']
            self.assertEqual(len(assocxtrsrcs_rows),1,
                             msg="No entries in assocxtrsrcs for image number "+str(imgs_loaded))
            self.assertEqual(assocxtrsrcs_rows[0]['runcat'], fixed_src_runcat_id,
                             "Mismatched runcat id in assocxtrsrc table")

        
    
class TestTransientCandidateMonitoring(unittest.TestCase):
    @requires_database()
    def setUp(self):
        import datetime
        self.database = tkpdb.DataBase()
        self.dataset = tkpdb.DataSet(data={'description':"Mon:"+self._testMethodName},
                                    database = self.database)

        self.n_images = 8                
        self.im_params = db_subs.example_dbimage_datasets(self.n_images)
        self.db_imgs=[]
        
        FixedSource = db_subs.example_extractedsource_tuple()            
        SlowTransient1 = FixedSource._replace(ra=123.888,
                                      peak = 5e-3, 
                                      flux = 5e-3,
                                      sigma = 4,
                                      )
        SlowTransient2 = SlowTransient1._replace(sigma = 3)    
        BrightFastTransient = FixedSource._replace(dec=15.666,
                                        peak = 30e-3,
                                        flux = 30e-3, 
                                        sigma = 15,
                                      )
        
        WeakFastTransient = FixedSource._replace(dec=15.777,
                                        peak = 10e-3,
                                        flux = 10e-3, 
                                        sigma = 5,
                                      )
        
            
        source_lists=[]
        for i in xrange(self.n_images):
            source_lists.append([FixedSource])
        
        source_lists[3].append(BrightFastTransient)
        
        source_lists[4].append(WeakFastTransient)        
        source_lists[5].append(SlowTransient1)
        source_lists[6].append(SlowTransient2)
                
        for i in xrange(self.n_images):
            self.db_imgs.append(
                        tkpdb.dataset.Image(data=self.im_params[i], 
                                            dataset=self.dataset)
                                )
            self.db_imgs[i].insert_extracted_sources(source_lists[i])
            self.db_imgs[i].associate_extracted_sources(deRuiter_r=3.7)
        
            
    def tearDown(self):
        self.database.close()

    def test_winkers(self):
        """test_winkers
        --- Tests the SQL call which finds sources not present in all epochs
        """
        
        winkers = db_utils.select_winking_sources(
                   self.database.connection,
                   self.dataset.id)
        self.assertEqual(len(winkers),3)
        self.assertEqual(winkers[0]['datapoints'],1)
        self.assertEqual(winkers[1]['datapoints'],1)
        self.assertEqual(winkers[2]['datapoints'],2)
        
    def test_candidate_thresholding(self):
        """test_candidate_thresholding
        ---Tests the SQL which selects sources based on detection SNR levels.
        """
        #Grab the source ids
        winkers = db_utils.select_winking_sources(
                   self.database.connection,
                   self.dataset.id)
        
        all_results = db_utils.select_transient_candidates_above_thresh(
                    self.database.connection, 
                    [c['runcat'] for c in winkers],
                    0,
                    0)
        self.assertEqual(len(winkers), len(all_results))
        
        bright_results = db_utils.select_transient_candidates_above_thresh(
                    self.database.connection, 
                    [c['runcat'] for c in winkers],
                    10,
                    10)
        self.assertEqual(len(bright_results), 1)
        self.assertEqual(bright_results[0]['max_det_sigma'], 15)
        
        #Should return bright single epoch, and fainter two epoch sources
        solid_results = db_utils.select_transient_candidates_above_thresh(
                    self.database.connection, 
                    [c['runcat'] for c in winkers],
                    3.5,
                    6.5)
        self.assertEqual(len(solid_results), 2)
        self.assertAlmostEqual(solid_results[1]['max_det_sigma'], 4)
        self.assertAlmostEqual(solid_results[1]['sum_det_sigma'], 7)
        
#        
    def test_full_transient_candidate_routine(self):
        all_results = self.dataset._find_transient_candidates(0,0)
        self.assertEqual(len(all_results),3)
        self.assertEqual(all_results[0]['datapoints'],1)
        self.assertEqual(all_results[1]['datapoints'],1)
        self.assertEqual(all_results[2]['datapoints'],2)
        self.assertAlmostEqual(all_results[2]['sum_det_sigma'], 7)
    
    def test_blind_source_monitoringlist_insertion_and_retrieval(self):
        """test_monitoringlist_insertion_and_retrieval

            We have faked transient sources for imgs
            3,4,5 and 6.
            
            In total we have 3 different fake transients.
            
            Therefore we should monitor all 3 in the imgs with
            only an extraction from the fixed source. 
        
        """
        self.dataset.mark_transient_candidates(0, 0)
        for dbimg in self.db_imgs[0:3]:
#            print "Image id:", dbimg.id
#            print "Monitor list:"
            srcs_to_monitor = dbimg.monitoringsources()
#            print srcs_to_monitor 
            self.assertEqual(len(srcs_to_monitor),3)
            
        for dbimg in self.db_imgs[3:7]:
#            print "Image id:", dbimg.id
#            print "Monitor list:" 
            srcs_to_monitor = dbimg.monitoringsources()
#            print srcs_to_monitor
            self.assertEqual(len(srcs_to_monitor),2)
            
    def test_monitored_source_insertion(self):
        """
        test_monitored_source_insertion
        
        - Test insertion of results for extractions caused by the monitoring list.
        - After monitoring is complete, we expect a full 8 datapoints for 
            each of our sources, whether fixed or transient. 
            (we fake non-detections for all the transient monitoring extractions) 
        """
        self.dataset.mark_transient_candidates(0, 0)
        for dbimg in self.db_imgs:
            srcs_to_monitor = dbimg.monitoringsources()
#           [( ra, dec, xtrsrcid , monitorid )]
            mon_extractions = []
            for src in srcs_to_monitor:
                mon_extractions.append(db_subs.ExtractedSourceTuple(ra=src[0], dec=src[1],
                                      ra_err=0.1, dec_err=0.1,
                                      peak = 0, peak_err = 5e-5,
                                      flux = 0, flux_err = 5e-5,
                                      sigma = 0,
                                      beam_maj = 100, beam_min = 100,
                                      beam_angle = 45
                                      )
                                )
            mon_results = [ (s[2],s[3],m) for  s,m in zip(srcs_to_monitor, mon_extractions)] 
            dbimg.insert_monitored_sources(mon_results)
#            
        runcat_rows = self.dataset.get_unique_source_ids()
#        print "Runcat rows:", runcat_rows
        self.assertEqual(len(runcat_rows), 4)
        assoc_counts = tkpdb.utils.count_associated_sources(self.database.connection,
                                   [r['xtrsrc'] for r in runcat_rows])
        for count in assoc_counts:
            self.assertEqual(count[1], 8)
#        print "Assoc counts:", assoc_counts
        
        
    def test_manual_monitoringlist_insertion(self):
        """test_manual_monitor_insertion
        
            Check that manually entered entries are dealt with correctly
        """
        tkpdb.utils.add_manual_entry_to_monitoringlist(
                       self.database.connection,
                       self.dataset.id, 
                       ra = 123.999,
                       dec = 15.999)
#        print "DSID:", self.dataset.id
        for dbimg in self.db_imgs:
            manual_srcs = tkpdb.utils.get_monitoringlist_not_observed_manual_entries(
                             self.database.connection,
                             dbimg.id, 
                             self.dataset.id)
            self.assertEqual(len(manual_srcs), 1)
            all_srcs_to_monitor = dbimg.monitoringsources()
            self.assertEqual(len(manual_srcs), len(all_srcs_to_monitor))
#            print "Monitor:", all_srcs_to_monitor
#            
#        
#    

#class TestLightCurve(unittest.TestCase):
#    """This test serves more as an example than as a proper unit
#    test
#    
#    TO DO: tidy this up a bit.
#    """        
#    def setUp(self):
#        import tkp.database
#        self.database = tkp.database.DataBase()
#
#    def tearDown(self):
#        self.database.close()
#    @requires_database()
#    def test_lightcurve(self):
#        """This test serves more as an example than as a proper unit
#        test"""
#        from tkp.database.dataset import DataSet
#        from tkp.database.dataset import Image
#        from tkp.database.dataset import ExtractedSource
#        import tkp.database.database
#        import monetdb
#        import datetime
#        from operator import attrgetter, itemgetter
#        dataset = DataSet(data={'description': 'dataset with images'},
#                          database=self.database)
#        # create 4 images, separated by one day each
#        images = [
#            Image(
#                dataset=dataset,
#                data={'taustart_ts': datetime.datetime(2010, 3, 3),
#                      'tau_time': 3600,
#                      'url': '/',
#                      'freq_eff': 80e6,
#                      'freq_bw': 1e6}),
#            Image(
#                dataset=dataset,
#                data={'taustart_ts': datetime.datetime(2010, 3, 4),
#                      'tau_time': 3600,
#                      'url': '/',
#                      'freq_eff': 80e6,
#                      'freq_bw': 1e6}),
#            Image(
#                dataset=dataset,
#                data={'taustart_ts': datetime.datetime(2010, 3, 5),
#                      'tau_time': 3600,
#                      'url': '/',
#                      'freq_eff': 80e6,
#                      'freq_bw': 1e6}),
#            Image(
#                dataset=dataset,
#                data={'taustart_ts': datetime.datetime(2010, 3, 6),
#                      'tau_time': 3600,
#                      'url': '/',
#                      'freq_eff': 80e6,
#                      'freq_bw': 1e6}),
#            ]
#        # 3 sources per image, with different coordinates & flux
#        data_list = [dict(ra=111.111*i, decl=11.11*i,
#                          ra_err=0.01, decl_err=0.01,
#                          i_peak=10*i, i_peak_err=0.1,
##                          x=0.11, y=0.22, z=0.33, det_sigma=11.1,
##                          zone=i
#                          )
#                     for i in range(1, 4)]
#        # Insert the 3 sources in each image, while further varying the flux
#        for i, image in enumerate(images):
#            # Create the "source finding results"
#            sources = [
#                (data['ra'], data['decl'], 
#                 data['ra_err'], data['decl_err'],
#                 data['i_peak']*(1+i), data['i_peak_err'],
#                 data['i_peak']*(1+i), data['i_peak_err'], 
#                 10.,#Significance level
#                 1, 1, 0) #Beam params (width arcsec major, width arcsec minor, parallactic angle) 
#                for data in data_list]
#            # Insert the sources
#            image.insert_extracted_sources(sources)
#            # Run the association for each list of source for an image
#            image.associate_extracted_sources()
#
#        # updates the dataset and its set of images
#        dataset.update()
#        dataset.update_images()
#        # update the images and their sets of sources
#        for image in dataset.images: 
#            image.update()
#            image.update_sources()
#        # Now pick any image, select the first source (smallest RA)
#        # and extract its light curve
#        sources = dataset.images.pop().sources
#        sources = sorted(sources, key=attrgetter('ra'))
#        lightcurve = sources[0].lightcurve()
#        self.assertEqual(lightcurve[0][0], datetime.datetime(2010, 3, 3, 0, 0))
#        self.assertEqual(lightcurve[1][0], datetime.datetime(2010, 3, 4, 0, 0))
#        self.assertEqual(lightcurve[2][0], datetime.datetime(2010, 3, 5, 0, 0))
#        self.assertEqual(lightcurve[3][0], datetime.datetime(2010, 3, 6, 0, 0))
#        self.assertAlmostEqual(lightcurve[0][2], 10.)
#        self.assertAlmostEqual(lightcurve[1][2], 20.)
#        self.assertAlmostEqual(lightcurve[2][2], 30.)
#        self.assertAlmostEqual(lightcurve[3][2], 40.)
#
#        # Since the light curves are very similar, only eta_nu is different
#        results = dataset.detect_variables()
#        results = sorted(results, key=itemgetter('eta_nu'))
#        for result, eta_nu in zip(results, (16666.66666667, 66666.666666667,
#                                            150000.0)):
#            self.assertEqual(result['npoints'], 4)
#            self.assertAlmostEqual(result['eta_nu'], eta_nu)
#            self.assertAlmostEqual(result['v_nu'], 0.516397779494)
            

    
