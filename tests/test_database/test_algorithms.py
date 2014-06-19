import unittest
from tkp.db.orm import DataSet, Image
import tkp.db
from tkp.testutil.decorators import requires_database
from tkp.testutil import db_subs
from tkp.db.generic import columns_from_table


class TestSourceAssociation(unittest.TestCase):
    @requires_database()
    def setUp(self):
        self.dataset = DataSet(data={'description': "Src. assoc:" +
                                                    self._testMethodName})

        self.im_params = db_subs.generate_timespaced_dbimages_data(n_images=8)
        self.db_imgs=[]

    def tearDown(self):
        tkp.db.rollback()


    def test_null_case_sequential(self):
        """test_null_case_sequential

        -Check extractedsource insertion routines can deal with empty input!
        -Check source association can too

        """
        for im in self.im_params:
            self.db_imgs.append(Image( data=im, dataset=self.dataset))
            self.db_imgs[-1].insert_extracted_sources([])
            self.db_imgs[-1].associate_extracted_sources(deRuiter_r=3.7)
            running_cat = columns_from_table(table="runningcatalog",
                                           keywords="*",
                                           where={"dataset":self.dataset.id})
            self.assertEqual(len(running_cat), 0)

#    def test_null_case_post_insert(self):
#        for im in self.im_params:
#            self.db_imgs.append( tkp.db.Image( data=im, dataset=self.dataset) )
#        pass

    def test_only_first_epoch_source(self):
        """test_only_first_epoch_source

        - Pretend to extract a source only from the first image.
        - Run source association for each image, as we would in TraP.
        - Check the image source listing works
        - Check runcat and assocxtrsource are correct.

        """


        first_epoch = True
        extracted_source_ids=[]
        for im in self.im_params:
            self.db_imgs.append( Image( data=im, dataset=self.dataset) )
            last_img =self.db_imgs[-1]

            if first_epoch:
                last_img.insert_extracted_sources([db_subs.example_extractedsource_tuple()])

            last_img.associate_extracted_sources(deRuiter_r=3.7)

            #First, check the runcat has been updated correctly:
            running_cat = columns_from_table(table="runningcatalog",
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
                assocxtrsrcs_rows = columns_from_table(table="assocxtrsource",
                                           keywords=['runcat', 'xtrsrc' ],
                                           where={"xtrsrc":img_xtrsrc_ids[0]})
                self.assertEqual(len(assocxtrsrcs_rows),1)
                self.assertEqual(assocxtrsrcs_rows[0]['xtrsrc'], img_xtrsrc_ids[0])
            else:
                self.assertEqual(len(img_xtrsrc_ids),0)

            first_epoch=False


        #Assocxtrsources still ok after multiple images?
        self.assertEqual(len(extracted_source_ids),1)
        assocxtrsrcs_rows = columns_from_table(table="assocxtrsource",
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
            self.db_imgs.append( Image( data=im, dataset=self.dataset) )
            last_img =self.db_imgs[-1]
            last_img.insert_extracted_sources([db_subs.example_extractedsource_tuple()])
            last_img.associate_extracted_sources(deRuiter_r=3.7)
            imgs_loaded+=1
            running_cat = columns_from_table(table="runningcatalog",
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
            assocxtrsrcs_rows = columns_from_table(table="assocxtrsource",
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


