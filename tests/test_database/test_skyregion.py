import unittest
if not  hasattr(unittest.TestCase, 'assertIsInstance'):
    import unittest2 as unittest
import tkp.database as tkpdb
import tkp.database.utils as dbutils
from tkp.testutil import db_subs
from tkp.testutil.decorators import requires_database, duration


@unittest.skip("Only need to test the basics if insertion SQL is altered.")
@duration(10) # requires deletion of the database for a clean test.
class TestSkyRegionBasics(unittest.TestCase):
    def shortDescription(self):
        return None #(Why define this? See http://goo.gl/xChvh )    
    @requires_database()
    def test_basic_insertion(self):
        """Here we begin with a single insertion, and check a relevant entry
        exists in the skyregion table.

        The key logic checked here is that inserting an image with duplicate
        skyregion will return the same skyrgn id as the first image of that field,
        conversely a new region results in a new skyrgn entry.

        """
        self.database = tkpdb.DataBase()
        db_subs.delete_test_database(self.database)

        self.dataset = tkpdb.DataSet(database=self.database,
                data={'description': "Skyrgn:" + self._testMethodName})
        n_images = 3
        im_params = db_subs.example_dbimage_datasets(n_images)

        ##First image:
        image0 = tkpdb.Image(dataset=self.dataset, data=im_params[0])
        image0.update()

        skyrgns = dbutils.columns_from_table(self.database.connection,
                     'skyregion', where={'dataset':self.dataset.id})
#        if self.clean_table:
        self.assertEqual(len(skyrgns), 1)
        rgn_keys = ['centre_ra', 'centre_decl', 'xtr_radius']
        first_skyrgn_id = None
        for db_row in skyrgns:
            if all([db_row[k] == im_params[0][k] for k in rgn_keys]):
                first_skyrgn_id = db_row['id']
        self.assertNotEqual(first_skyrgn_id, None)
        self.assertEqual(image0._data['skyrgn'], first_skyrgn_id)

        ##Second, identical image:
        image1 = tkpdb.Image(dataset=self.dataset, data=im_params[1])
        image1.update()
        self.assertEqual(image1._data['skyrgn'], first_skyrgn_id)

        ##Third, different image:
        im_params[2]['centre_ra'] += im_params[2]['xtr_radius'] * 0.5
        image2 = tkpdb.Image(dataset=self.dataset, data=im_params[2])
        image2.update()
        self.assertNotEqual(image2._data['skyrgn'], first_skyrgn_id)
        skyrgns = dbutils.columns_from_table(self.database.connection,
                             'skyregion', where={'dataset':self.dataset.id})
        for db_row in skyrgns:
            if all([db_row[k] == im_params[2][k] for k in rgn_keys]):
                second_skyrgn_id = db_row['id']
        self.assertNotEqual(second_skyrgn_id, None)
        self.assertEqual(image2._data['skyrgn'], second_skyrgn_id)

class TestSkyRegionAssociation(unittest.TestCase):
    """Test whether skyregions are correctly associated to runcat sources"""
    def shortDescription(self):
         return None #(Why define this? See http://goo.gl/xChvh )
    @requires_database()
    def setUp(self):
        self.database = tkpdb.DataBase()
        self.dataset = tkpdb.DataSet(database=self.database,
                data={'description': "Skyrgn:" + self._testMethodName})
#    @unittest.skip("Skipping")
    def test_new_skyregion_insertion(self):
        """Here we test the association logic executed upon insertion of a 
        new skyregion. 

        We expect that any pre-existing entries in the runningcatalog
        which lie within the field of view will be marked as 
        'within this region', through the presence of an entry in table 
        ``assocskyrgn``. 
        Conversely sources outside the FoV should not be marked as related.
        
        We begin with img0, with a source at centre.
        Then we add 2 more (empty) images/fields at varying positions.
        """
        n_images = 6
        im_params = db_subs.example_dbimage_datasets(n_images)

        src_in_img0 = db_subs.example_extractedsource_tuple(
                        ra=im_params[0]['centre_ra'],
                        dec=im_params[0]['centre_decl'],)

        ##First image:
        image0 = tkpdb.Image(dataset=self.dataset, data=im_params[0])
        image0.insert_extracted_sources([src_in_img0])
        image0.associate_extracted_sources(deRuiter_r=3.7)
        image0.update()

        runcats = dbutils.columns_from_table(self.database.connection,
                                'runningcatalog',
                                where={'dataset':self.dataset.id})
        self.assertEqual(len(runcats), 1) #Just a sanity check.
        ##Second, different *But overlapping* image:
        idx = 1
        im_params[idx]['centre_decl'] += im_params[idx]['xtr_radius'] * 0.9
        image1 = tkpdb.Image(dataset=self.dataset, data=im_params[idx])
        image1.update()

        assocs = dbutils.columns_from_table(self.database.connection,
                         'assocskyrgn', where={'skyrgn':image1._data['skyrgn']})
        self.assertEqual(len(assocs), 1)
        self.assertEqual(assocs[0]['runcat'], runcats[0]['id'])

        ##Third, different *and NOT overlapping* image:
        idx = 2
        im_params[idx]['centre_decl'] += im_params[idx]['xtr_radius'] * 1.1
        image2 = tkpdb.Image(dataset=self.dataset, data=im_params[idx])
        image2.update()
        assocs = dbutils.columns_from_table(self.database.connection,
                         'assocskyrgn', where={'skyrgn':image2._data['skyrgn']})
        self.assertEqual(len(assocs), 0)

#    @unittest.skip("Skipping")
    def test_new_runcat_insertion(self):
        """Here we test the association logic executed upon insertion of a 
        new runningcatalog source. 
        
        We add an empty image0, then proceed to image1, 
        which is partially overlapping.
        We add one new overlapping source, and one source only in image1's skyrgn.
        Then we check that the back-associations to image0 are correct.
        """
        n_images = 6
        im_params = db_subs.example_dbimage_datasets(n_images)

        #We first create 2 overlapping images, 
        #one above the other in dec by 1.0*xtr_radius
        idx = 0
        image0 = tkpdb.Image(dataset=self.dataset, data=im_params[idx])
        image0.update()

        idx = 1
        im_params[idx]['centre_decl'] += im_params[idx]['xtr_radius']
        #We place one source half-way between the field centres (i.e. in both)
        src_in_imgs_0_1 = db_subs.example_extractedsource_tuple(
                                    ra=im_params[idx]['centre_ra'],
                                    dec=im_params[idx]['centre_decl'] -
                                            im_params[idx]['xtr_radius'] * 0.5)

        #And one source only in field 1
        src_in_img_1_only = db_subs.example_extractedsource_tuple(
                        ra=im_params[idx]['centre_ra'],
                        dec=im_params[idx]['centre_decl'] +
                            im_params[idx]['xtr_radius'] * 0.5)

        ##First insert new sources in img1 and check association to parent field:
        ## (This is always asserted without calculation, for efficiency)
        image1 = tkpdb.Image(dataset=self.dataset, data=im_params[1])
        image1.insert_extracted_sources([src_in_imgs_0_1, src_in_img_1_only])
        image1.associate_extracted_sources(deRuiter_r=3.7)
        image1.update()

        runcats = dbutils.columns_from_table(self.database.connection,
                        'runningcatalog',
                        where={'dataset':self.dataset.id})

        #We now expect to see both runcat entries in the field of im1 
        im1_assocs = dbutils.columns_from_table(self.database.connection,
                         'assocskyrgn', where={'skyrgn':image1._data['skyrgn']})

        self.assertEqual(len(im1_assocs), 2)
        self.assertEqual(im1_assocs[0]['runcat'], runcats[0]['id'])
        self.assertEqual(im1_assocs[1]['runcat'], runcats[1]['id'])

        #But only one in field of im0 ( the first source).
        im0_assocs = dbutils.columns_from_table(self.database.connection,
                         'assocskyrgn', where={'skyrgn':image0._data['skyrgn']})

        self.assertEqual(len(im0_assocs), 1)
        self.assertEqual(im0_assocs[0]['runcat'], runcats[0]['id'])

class TestOneToManyAssocUpdates(unittest.TestCase):
    """Check assocsky updates are made correctly when the runningcatalog forks.
    """
    def shortDescription(self):
         return None #(Why define this? See http://goo.gl/xChvh )
    @requires_database()
    def setUp(self):
        self.database = tkpdb.DataBase()
        self.dataset = tkpdb.DataSet(database=self.database,
                data={'description': "Skyrgn:" + self._testMethodName})
#    @unittest.skip("Skipping")
    def test_basic_same_field_case(self):
        """ Here we start with 1 source in image0.
        We then add image1 (same field as image0), with a double association 
        for the source, and check assocskyrgn updates correctly. 
       """
        n_images = 2
        im_params = db_subs.example_dbimage_datasets(n_images)

        idx = 0
        src_a = db_subs.example_extractedsource_tuple(
                        ra=im_params[idx]['centre_ra'],
                        dec=im_params[idx]['centre_decl'])

        src_b = src_a._replace(ra=src_a.ra + 1. / 60.) # 1 arcminute offset
        imgs = []
        imgs.append(tkpdb.Image(dataset=self.dataset, data=im_params[idx]))
        imgs[idx].insert_extracted_sources([src_a])
        imgs[idx].associate_extracted_sources(deRuiter_r=3.7)

        idx = 1
        imgs.append(tkpdb.Image(dataset=self.dataset, data=im_params[idx]))
        imgs[idx].insert_extracted_sources([src_a, src_b])
        imgs[idx].associate_extracted_sources(deRuiter_r=3.7)
        imgs[idx].update()
        runcats = dbutils.columns_from_table(self.database.connection,
                                'runningcatalog',
                                where={'dataset':self.dataset.id})
        self.assertEqual(len(runcats), 2) #Just a sanity check.
        skyassocs = dbutils.columns_from_table(self.database.connection,
                         'assocskyrgn', where={'skyrgn':imgs[idx]._data['skyrgn']})
        self.assertEqual(len(skyassocs), 2)
