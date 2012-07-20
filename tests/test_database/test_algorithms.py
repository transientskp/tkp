import unittest
import logging
    
import tkp.database as tkpdb
from .. import db_subs
from ..decorators import requires_database
import tkp.database.utils as db_utils
import tkp.tests.db_subs as db_subs
from tkp.tests.decorators import requires_database

class TestSourceAssociation(unittest.TestCase):
    @requires_database()
    def setUp(self):
    
        self.database = tkpdb.DataBase()
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
#    
    def test_only_first_epoch_source(self):
        first_epoch = True
        extracted_source_ids=[]
        for im in self.im_params:
            self.db_imgs.append( tkpdb.dataset.Image( data=im, dataset=self.dataset) )
            last_img =self.db_imgs[-1] 
            
            if first_epoch:
                last_img.insert_extracted_sources([db_subs.example_extractedsource_tuple()])
                
            last_img.associate_extracted_sources()
            
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
        self.assertEqual(assocxtrsrcs_rows[0]['runcat'], extracted_source_ids[0])
            
#            print "First epoch DSID",self.dataset.id
#            print "Runcat:", running_cat

    def test_single_fixed_source(self):
        imgs_loaded = 0
        ds_source_ids=[]
        for im in self.im_params:
            self.db_imgs.append( tkpdb.dataset.Image( data=im, dataset=self.dataset) )
            last_img =self.db_imgs[-1]
            last_img.insert_extracted_sources([db_subs.example_extractedsource_tuple()])
            last_img.associate_extracted_sources()
            imgs_loaded+=1
            running_cat = tkpdb.utils.columns_from_table(self.database.connection,
                                           table="runningcatalog",
                                           keywords=['datapoints'],
                                           where={"dataset":self.dataset.id})
            self.assertEqual(len(running_cat), 1)
            self.assertEqual(running_cat[0]['datapoints'], imgs_loaded)               
            last_img.update()
            last_img.update_sources()
            img_xtrsrc_ids = [src.id for src in last_img.sources]
            self.assertEqual(len(img_xtrsrc_ids), 1)
            ds_source_ids.extend(img_xtrsrc_ids)
            assocxtrsrcs_rows = tkpdb.utils.columns_from_table(self.database.connection,
                                       table="assocxtrsource",
                                       keywords=['runcat', 'xtrsrc' ],
                                       where={"xtrsrc":img_xtrsrc_ids[0]})
#            print "ImageID:", last_img.id
#            print "Imgs sources:", img_xtrsrc_ids
#            print "Assoc entries:", assocxtrsrcs_rows 
#            print "First extracted source id:", ds_source_ids[0]
#            if len(assocxtrsrcs_rows):
#                print "Associated source:", assocxtrsrcs_rows[0]['xtrsrc_id']
            
            self.assertEqual(len(assocxtrsrcs_rows),1,
                             msg="No entries in assocxtrsrcs for image number "+str(imgs_loaded))
            self.assertEqual(assocxtrsrcs_rows[0]['xtrsrc_id'], ds_source_ids[0],
                             msg="Assocxtrsrcs table incorrectly assocating for image number "
                             +str(imgs_loaded))

        
    
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
        #Grab the source ids
        winkers = db_utils.select_winking_sources(
                   self.database.connection,
                   self.dataset.id)
        
        all_results = db_utils.select_transient_candidates_above_thresh(
                    self.database.connection, 
                    [c['xtrsrc_id'] for c in winkers],
                    0,
                    0)
        self.assertEqual(len(winkers), len(all_results))
        
        bright_results = db_utils.select_transient_candidates_above_thresh(
                    self.database.connection, 
                    [c['xtrsrc_id'] for c in winkers],
                    10,
                    10)
        self.assertEqual(len(bright_results), 1)
        self.assertEqual(bright_results[0]['max_det_sigma'], 15)
        
        #Should return bright single epoch, and fainter two epoch sources
        solid_results = db_utils.select_transient_candidates_above_thresh(
                    self.database.connection, 
                    [c['xtrsrc_id'] for c in winkers],
                    3.5,
                    6.5)
        self.assertEqual(len(solid_results), 2)
        self.assertAlmostEqual(solid_results[1]['max_det_sigma'], 4)
        self.assertAlmostEqual(solid_results[1]['sum_det_sigma'], 7)
        
        
    def test_full_transient_candidate_routine(self):
        all_results = self.dataset.find_transient_candidates(0,0)
        self.assertEqual(len(all_results),3)
#        self.assertEqual(results[0]['datapoints'],1)
#        self.assertEqual(results[1]['datapoints'],1)
        self.assertEqual(all_results[2]['datapoints'],2)
        self.assertAlmostEqual(all_results[2]['sum_det_sigma'], 7)
    
    
    def test_monitoringlist_insertion(self):
        pass
    


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
            

    
