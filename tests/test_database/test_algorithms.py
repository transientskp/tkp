import unittest
import logging
#try:
#    unittest.TestCase.assertIsInstance
#except AttributeError:
#    import unittest2 as unittest
#    
logging.basicConfig(level=logging.CRITICAL)

import tkp.database as tkpdb
from .. import db_subs
from ..decorators import requires_database

class TestSourceAssociation(unittest.TestCase):
    @requires_database()
    def setUp(self):
    
        self.database = tkpdb.DataBase()
        self.dataset = tkpdb.DataSet(data={'inname':"Source assoc. test"},
                                                    database = self.database)
        
        self.im_params = db_subs.example_dbimage_datasets(n_images=8)
        self.db_imgs=[]
        
    
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
                                           table="assocxtrsources",
                                           keywords=['xtrsrc_id', 'assoc_xtrsrc_id' ],
                                           where={"assoc_xtrsrc_id":img_xtrsrc_ids[0]})
                self.assertEqual(len(assocxtrsrcs_rows),1)
                self.assertEqual(assocxtrsrcs_rows[0]['xtrsrc_id'], img_xtrsrc_ids[0])
            else:
                self.assertEqual(len(img_xtrsrc_ids),0)
            
            first_epoch=False
            
        
        #Assocxtrsources still ok after multiple images?
        self.assertEqual(len(extracted_source_ids),1)
        assocxtrsrcs_rows = tkpdb.utils.columns_from_table(self.database.connection,
                                           table="assocxtrsources",
                                           keywords=['xtrsrc_id', 'assoc_xtrsrc_id' ],
                                           where={"assoc_xtrsrc_id":extracted_source_ids[0]})
        self.assertEqual(len(assocxtrsrcs_rows),1)
        self.assertEqual(assocxtrsrcs_rows[0]['xtrsrc_id'], extracted_source_ids[0])
            
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
                                       table="assocxtrsources",
                                       keywords=['xtrsrc_id', 'assoc_xtrsrc_id' ],
                                       where={"assoc_xtrsrc_id":img_xtrsrc_ids[0]})
#            print "ImageID:", last_img.id
#            print "Imgs sources:", img_xtrsrc_ids
#            print "Assoc entries:", assocxtrsrcs_rows 
#            print "First extracted source id:", ds_source_ids[0]
#            if len(assocxtrsrcs_rows):
#                print "Associated source:", assocxtrsrcs_rows[0]['xtrsrc_id']
            
            self.assertEqual(len(assocxtrsrcs_rows),1,
                             msg="No entries in assocxtrsrcs for image number "+str(imgs_loaded))
#            self.assertEqual(assocxtrsrcs_rows[0]['xtrsrc_id'], ds_source_ids[0],
#                             msg="Assocxtrsrcs table incorrectly assocating for image number "
#                             +str(imgs_loaded)")
            
            
            

        
    
class TestMonitoringlistFunctionality(unittest.TestCase):
    @requires_database()
    def setUp(self):
        import datetime
        self.database = tkpdb.DataBase()
        self.dataset = tkpdb.DataSet(data={'inname':"Test Dataset"},
                                                    database = self.database)

        self.n_images = 8                
        self.im_params = db_subs.example_dbimage_datasets(self.n_images)
        self.db_imgs=[]
        for im in self.im_params:
            self.db_imgs.append( tkpdb.dataset.Image( data=im, dataset=self.dataset) )
            
            
        FixedSource = db_subs.example_extractedsource_tuple()
        
        SlowTransient = FixedSource._replace(ra=128.123,
                                      peak = 5e-3, 
                                      flux = 5e-3,
                                      sigma = 5,
                                      )
        
        FastTransient = FixedSource._replace(dec=15.5,
                                        peak = 10e-3,
                                        flux = 10e-3, 
                                        sigma = 10,
                                      )
        source_lists=[]
        for i in xrange(self.n_images):
            source_lists.append([ FixedSource ])
        
        source_lists[3].append(FastTransient)
                
        source_lists[5].append(SlowTransient)
        source_lists[6].append(SlowTransient)
        
#        for i in xrange(n_images):
#            self.db_imgs[i].insert_extracted_sources(source_lists[i])
#            self.db_imgs[i].associate_extracted_sources(deRuiter_r=3.7)
        
            
    def tearDown(self):
        self.database.close()
            
        
    def testSetUp(self):
        pass
#        print "Test dataset has been set up."
#        print "Dataset id:", self.dataset.id
#        print "Image ids:", [img.id for img in self.db_imgs]
#        for img in self.db_imgs:
#            img.update()
#            self.assertEqual(img.tau_time, self.im_params[0]['tau_time'])

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
#        dataset = DataSet(data={'dsinname': 'dataset with images'},
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
            

    
