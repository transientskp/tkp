import unittest
import tkp.db
from tkp.db import nd as dbnd
from tkp.testutil import db_subs
from tkp.testutil.decorators import requires_database, duration
from tkp.db.generic import columns_from_table, get_db_rows_as_dicts


@unittest.skip("Only need to test the basics if insertion SQL is altered.")
@duration(10) # requires deletion of the database for a clean test, which takes time.
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
        self.database = tkp.db.Database()
        db_subs.delete_test_database(self.database)

        self.dataset = tkp.db.DataSet(database=self.database,
                data={'description': "Skyrgn:" + self._testMethodName})
        n_images = 3
        im_params = db_subs.example_dbimage_datasets(n_images)

        ##First image:
        image0 = tkp.db.Image(dataset=self.dataset, data=im_params[0])
        image0.update()

        skyrgns = columns_from_table('skyregion',
                                             where={'dataset':self.dataset.id})
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
        image1 = tkp.db.Image(dataset=self.dataset, data=im_params[1])
        image1.update()
        self.assertEqual(image1._data['skyrgn'], first_skyrgn_id)

        ##Third, different image:
        im_params[2]['centre_ra'] += im_params[2]['xtr_radius'] * 0.5
        image2 = tkp.db.Image(dataset=self.dataset, data=im_params[2])
        image2.update()
        self.assertNotEqual(image2._data['skyrgn'], first_skyrgn_id)
        skyrgns = columns_from_table('skyregion',
                                             where={'dataset':self.dataset.id})
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
        self.database = tkp.db.Database()
        self.dataset = tkp.db.DataSet(database=self.database,
                data={'description': "Skyrgn:" + self._testMethodName})


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
        image0 = tkp.db.Image(dataset=self.dataset, data=im_params[0])
        image0.insert_extracted_sources([src_in_img0])
        image0.associate_extracted_sources(deRuiter_r=3.7)
        image0.update()

        runcats = columns_from_table('runningcatalog',
                                where={'dataset':self.dataset.id})
        self.assertEqual(len(runcats), 1) #Just a sanity check.
        ##Second, different *But overlapping* image:
        idx = 1
        im_params[idx]['centre_decl'] += im_params[idx]['xtr_radius'] * 0.9
        image1 = tkp.db.Image(dataset=self.dataset, data=im_params[idx])
        image1.update()

        assocs = columns_from_table('assocskyrgn',
                                    where={'skyrgn':image1._data['skyrgn']})
        self.assertEqual(len(assocs), 1)
        self.assertEqual(assocs[0]['runcat'], runcats[0]['id'])

        ##Third, different *and NOT overlapping* image:
        idx = 2
        im_params[idx]['centre_decl'] += im_params[idx]['xtr_radius'] * 1.1
        image2 = tkp.db.Image(dataset=self.dataset, data=im_params[idx])
        image2.update()
        assocs = columns_from_table('assocskyrgn',
                                    where={'skyrgn':image2._data['skyrgn']})
        self.assertEqual(len(assocs), 0)

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
        image0 = tkp.db.Image(dataset=self.dataset, data=im_params[idx])
        image0.update()

        #Bump up the centre of img1 to higher declination
        im_params[1]['centre_decl'] += im_params[1]['xtr_radius']
        #We place one source half-way between the field centres (i.e. in both)
        src_in_imgs_0_1 = db_subs.example_extractedsource_tuple(
                                    ra=im_params[1]['centre_ra'],
                                    dec=im_params[1]['centre_decl'] -
                                            im_params[1]['xtr_radius'] * 0.5)

        #And one source only in field 1
        src_in_img_1_only = db_subs.example_extractedsource_tuple(
                        ra=im_params[1]['centre_ra'],
                        dec=im_params[1]['centre_decl'] +
                            im_params[1]['xtr_radius'] * 0.5)

        ##First insert new sources in img1 and check association to parent field:
        ## (This is always asserted without calculation, for efficiency)
        image1 = tkp.db.Image(dataset=self.dataset, data=im_params[1])
        image1.insert_extracted_sources([src_in_imgs_0_1, src_in_img_1_only])
        image1.associate_extracted_sources(deRuiter_r=3.7)
        image1.update()

        runcats = columns_from_table('runningcatalog',
                        where={'dataset':self.dataset.id})

        #We now expect to see both runcat entries in the field of im1
        im1_assocs = columns_from_table('assocskyrgn',
                                    where={'skyrgn':image1._data['skyrgn']})
        self.assertEqual(len(im1_assocs), 2)
        runcat_ids = [r['id'] for r in  runcats]
        for assoc in im1_assocs:
            self.assertTrue(assoc['runcat'] in runcat_ids)

        #The new sources are *also checked against previous regions*
        #Only expect one in field of im0 ( the first source).
        im0_assocs = columns_from_table('assocskyrgn',
                                    where={'skyrgn':image0._data['skyrgn']})

        runcats_only_in_im0 = columns_from_table('runningcatalog',
                                        where={'dataset':self.dataset.id,
                                               'wm_decl':15})

        self.assertEqual(len(im0_assocs), 1)
        self.assertEqual(len(runcats_only_in_im0), 1)
        self.assertEqual(im0_assocs[0]['runcat'], runcats_only_in_im0[0]['id'])


class TestOneToManyAssocUpdates(unittest.TestCase):
    """Check assocsky updates are made correctly when the runningcatalog forks.
    """
    def shortDescription(self):
         return None #(Why define this? See http://goo.gl/xChvh )

    @requires_database()
    def setUp(self):
        self.database = tkp.db.Database()
        self.dataset = tkp.db.DataSet(database=self.database,
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
        imgs.append(tkp.db.Image(dataset=self.dataset, data=im_params[idx]))
        imgs[idx].insert_extracted_sources([src_a])
        imgs[idx].associate_extracted_sources(deRuiter_r=3.7)

        idx = 1
        imgs.append(tkp.db.Image(dataset=self.dataset, data=im_params[idx]))
        imgs[idx].insert_extracted_sources([src_a, src_b])
        imgs[idx].associate_extracted_sources(deRuiter_r=3.7)
        imgs[idx].update()
        runcats = columns_from_table('runningcatalog',
                                where={'dataset':self.dataset.id})
        self.assertEqual(len(runcats), 2) #Just a sanity check.
        skyassocs = columns_from_table('assocskyrgn',
                                   where={'skyrgn':imgs[idx]._data['skyrgn']})
        self.assertEqual(len(skyassocs), 2)


class TestTransientExclusion(unittest.TestCase):
    def shortDescription(self):
        return None #(Why define this? See http://goo.gl/xChvh )

    @requires_database()
    def setUp(self):
        self.database = tkp.db.Database()
        self.dataset = tkp.db.DataSet(database=self.database,
                data={'description': "Skyrgn:" + self._testMethodName})

    def test_two_field_basic_case(self):
        """Here we create 2 disjoint image fields, with one source in each,
        and check that the second source inserted does not get flagged as transient.
        """
        n_images = 2
        xtr_radius = 1.5
        im_params = db_subs.example_dbimage_datasets(n_images,
                                                     xtr_radius=xtr_radius)
        im_params[1]['centre_decl'] += xtr_radius * 2 + 0.5

        imgs = []
        for idx in range(len(im_params)):
            imgs.append(tkp.db.Image(dataset=self.dataset, data=im_params[idx]))

        for idx in range(len(im_params)):
            central_src = db_subs.example_extractedsource_tuple(
                                    ra=im_params[idx]['centre_ra'],
                                    dec=im_params[idx]['centre_decl'])

            imgs.append(tkp.db.Image(dataset=self.dataset, data=im_params[idx]))
            imgs[idx].insert_extracted_sources([central_src])
            imgs[idx].associate_extracted_sources(deRuiter_r=3.7)

        runcats = columns_from_table('runningcatalog',
                                where={'dataset':self.dataset.id})

        self.assertEqual(len(runcats), 2) #Just a sanity check.

        transients_qry = """\
        SELECT *
          FROM transient tr
              ,runningcatalog rc
        WHERE rc.dataset = %s
          AND tr.runcat = rc.id
        """
        self.database.cursor.execute(transients_qry, (self.dataset.id,))
        transients = get_db_rows_as_dicts(self.database.cursor)
        self.assertEqual(len(transients), 0)

    def test_two_field_overlap_new_transient(self):
        """Now for something more interesting - two overlapping fields, 4 sources:
        one steady source only in lower field,
        one steady source in both fields,
        one steady source only in upper field,
        one transient source in both fields but only at 2nd timestep.
        """
        n_images = 2
        xtr_radius = 1.5
        im_params = db_subs.example_dbimage_datasets(n_images,
                                                     xtr_radius=xtr_radius)
        im_params[1]['centre_decl'] += xtr_radius * 1

        imgs = []

        lower_steady_src = db_subs.example_extractedsource_tuple(
                                ra=im_params[0]['centre_ra'],
                                dec=im_params[0]['centre_decl'] - 0.5 * xtr_radius)
        upper_steady_src = db_subs.example_extractedsource_tuple(
                                ra=im_params[1]['centre_ra'],
                                dec=im_params[1]['centre_decl'] + 0.5 * xtr_radius)
        overlap_steady_src = db_subs.example_extractedsource_tuple(
                                ra=im_params[0]['centre_ra'],
                                dec=im_params[0]['centre_decl'] + 0.2 * xtr_radius)
        overlap_transient = db_subs.example_extractedsource_tuple(
                                ra=im_params[0]['centre_ra'],
                                dec=im_params[0]['centre_decl'] + 0.8 * xtr_radius)

        imgs.append(tkp.db.Image(dataset=self.dataset, data=im_params[0]))
        imgs.append(tkp.db.Image(dataset=self.dataset, data=im_params[1]))

        imgs[0].insert_extracted_sources([lower_steady_src, overlap_steady_src])
        imgs[0].associate_extracted_sources(deRuiter_r=0.1)
        nd_posns = dbnd.get_nulldetections(imgs[0].id)
        self.assertEqual(len(nd_posns), 0)

        imgs[1].insert_extracted_sources([upper_steady_src, overlap_steady_src,
                                          overlap_transient])
        imgs[1].associate_extracted_sources(deRuiter_r=0.1)
        nd_posns = dbnd.get_nulldetections(imgs[1].id)
        self.assertEqual(len(nd_posns), 0)

        runcats = columns_from_table('runningcatalog',
                                where={'dataset': self.dataset.id})
        self.assertEqual(len(runcats), 4) #sanity check.

        transients_qry = """\
        SELECT *
          FROM transient tr
              ,runningcatalog rc
        WHERE rc.dataset = %s
          AND tr.runcat = rc.id
        """
        self.database.cursor.execute(transients_qry, (self.dataset.id,))
        transients = get_db_rows_as_dicts(self.database.cursor)
        self.assertEqual(len(transients), 1)

    def test_two_field_overlap_nulling_src(self):
        """Similar to above, but one source disappears:
        Two overlapping fields, 4 sources:
        one steady source only in lower field,
        one steady source in both fields,
        one steady source only in upper field,
        one transient source in both fields but only at *1st* timestep.
        """
        n_images = 2
        xtr_radius = 1.5
        im_params = db_subs.example_dbimage_datasets(n_images,
                                                     xtr_radius=xtr_radius)
        im_params[1]['centre_decl'] += xtr_radius * 1

        imgs = []

        lower_steady_src = db_subs.example_extractedsource_tuple(
                                ra=im_params[0]['centre_ra'],
                                dec=im_params[0]['centre_decl'] - 0.5 * xtr_radius)
        upper_steady_src = db_subs.example_extractedsource_tuple(
                                ra=im_params[1]['centre_ra'],
                                dec=im_params[1]['centre_decl'] + 0.5 * xtr_radius)
        overlap_steady_src = db_subs.example_extractedsource_tuple(
                                ra=im_params[0]['centre_ra'],
                                dec=im_params[0]['centre_decl'] + 0.2 * xtr_radius)
        overlap_transient = db_subs.example_extractedsource_tuple(
                                ra=im_params[0]['centre_ra'],
                                dec=im_params[0]['centre_decl'] + 0.8 * xtr_radius)

        imgs.append(tkp.db.Image(dataset=self.dataset, data=im_params[0]))
        imgs.append(tkp.db.Image(dataset=self.dataset, data=im_params[1]))

        imgs[0].insert_extracted_sources([lower_steady_src, overlap_steady_src,
                                          overlap_transient])
        imgs[0].associate_extracted_sources(deRuiter_r=0.1)
        nd_posns = dbnd.get_nulldetections(imgs[0].id)
        self.assertEqual(len(nd_posns), 0)

        imgs[1].insert_extracted_sources([upper_steady_src, overlap_steady_src])

        imgs[1].associate_extracted_sources(deRuiter_r=0.1)
        #This time we don't expect to get an immediate transient detection,
        #but we *do* expect to get a null-source forced extraction request:
        nd_posns = dbnd.get_nulldetections(imgs[1].id)
        self.assertEqual(len(nd_posns), 1)

        runcats = columns_from_table('runningcatalog',
                                where={'dataset':self.dataset.id})
        self.assertEqual(len(runcats), 4) #sanity check.




