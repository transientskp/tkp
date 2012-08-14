import unittest
if not  hasattr(unittest.TestCase, 'assertIsInstance'):
    import unittest2 as unittest
import tkp.database as tkpdb
from tkp.classification.transient import Transient
import tkp.config
import db_subs
from decorators import requires_database


@unittest.skipIf(not eval(tkp.config.config['test']['long']), "not runnig prolonged test suite")
class TestTransientRoutines(unittest.TestCase):
    @requires_database()
    def setUp(self):
        self.database = tkpdb.DataBase()
        self.dataset = tkpdb.DataSet(data={'description':"Trans:"+self._testMethodName},
                                    database = self.database)

        self.n_images = 8                
        self.im_params = db_subs.example_dbimage_datasets(self.n_images)
        self.db_imgs=[]
        
        #Insert transient source extractions, 
        #Include the non-detection points we expect from using monitoringlist:
        source_lists=db_subs.example_source_lists(n_images=8,
                                                  include_non_detections=True)
                    
        for i in xrange(self.n_images):
            self.db_imgs.append(
                        tkpdb.Image(data=self.im_params[i], 
                                            dataset=self.dataset)
                                )
            self.db_imgs[i].insert_extracted_sources(source_lists[i])
            self.db_imgs[i].associate_extracted_sources(deRuiter_r=3.7)
            
        runcats = self.dataset.runcat_entries()
        self.assertNotEqual(len(runcats),0)
        arbitrary_valid_rcid = runcats[0]['runcat']
        self.dummy_transient = Transient(runcatid = arbitrary_valid_rcid)
        self.dummy_transient.eta = 2 #Reduced Chi-squared
        self.dummy_transient.V = 0.5 #Fractional std. dev.
            
    def tearDown(self):
        self.database.close()
        
    def test_insertion_with_no_images(self):
        tkpdb.utils.insert_transient(self.database.connection,
                                     self.dummy_transient,
                                     self.dataset.id,
                                     image_ids=None)
        
    def test_insertion_with_one_image(self):
        image_ids = [ self.db_imgs[-1].id ] 
        tkpdb.utils.insert_transient(self.database.connection,
                                     self.dummy_transient,
                                     self.dataset.id,
                                     image_ids=image_ids)
        
    def test_insertion_with_multiple_images(self):
        image_ids = [ img.id for img in  self.db_imgs[0:4] ] 
        tkpdb.utils.insert_transient(self.database.connection,
                                     self.dummy_transient,
                                     self.dataset.id,
                                     image_ids=image_ids)

    def test_full_transient_search_routine(self):
        tkpdb.utils.transient_search(
                     conn = self.database.connection,
                     dataset = self.dataset, 
                     eta_lim = 1.1,
                     V_lim = 0.01,
                     probability_threshold = 0.01, 
                     minpoints = 1)
        
        
        
