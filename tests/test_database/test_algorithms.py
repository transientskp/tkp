from builtins import str
import unittest
from tkp.db.orm import DataSet, Image
import tkp.db
import tkp.db.database
from tkp.db.associations import associate_extracted_sources
from tkp.db.general import insert_extracted_sources
from tkp.testutil.decorators import requires_database
from tkp.testutil import db_subs
from tkp.db.generic import columns_from_table

# Convenient default values
deRuiter_r = 3.7
new_source_sigma_margin = 3


class TestSourceAssociation(unittest.TestCase):
    @requires_database()
    def setUp(self):
        self.database = tkp.db.database.Database()
        self.dataset = DataSet(data={'description': "Src. assoc:" +
                                                    self._testMethodName},
                               database=self.database)

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
            self.db_imgs.append(Image(data=im, dataset=self.dataset))
            insert_extracted_sources(self.db_imgs[-1]._id, [],'blind')
            associate_extracted_sources(self.db_imgs[-1]._id, deRuiter_r,
                                        new_source_sigma_margin)
            running_cat = columns_from_table(table="runningcatalog",
                                             keywords="*",
                                             where={"dataset":self.dataset.id})
            self.assertEqual(len(running_cat), 0)

    def test_only_first_epoch_source(self):
        """test_only_first_epoch_source

        - Pretend to extract a source only from the first image.
        - Run source association for each image, as we would in TraP.
        - Check the image source listing works
        - Check runcat and assocxtrsource are correct.

        """
        first_epoch = True
        extracted_source_ids = []
        for im in self.im_params:
            self.db_imgs.append(Image( data=im, dataset=self.dataset))
            last_img = self.db_imgs[-1]

            if first_epoch:
                insert_extracted_sources(last_img._id,
                    [db_subs.example_extractedsource_tuple()], 'blind')

            associate_extracted_sources(last_img._id, deRuiter_r,
                                        new_source_sigma_margin)

            # First, check the runcat has been updated correctly
            running_cat = columns_from_table(table="runningcatalog",
                                             keywords=['datapoints'],
                                             where={"dataset": self.dataset.id})
            self.assertEqual(len(running_cat), 1)
            self.assertEqual(running_cat[0]['datapoints'], 1)

            last_img.update()
            last_img.update_sources()
            img_xtrsrc_ids = [src.id for src in last_img.sources]

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

        fixed_src_runcat_id = None
        for img_idx, im in enumerate(self.im_params):
            self.db_imgs.append( Image(data=im, dataset=self.dataset))
            last_img = self.db_imgs[-1]
            insert_extracted_sources(last_img._id,
                [db_subs.example_extractedsource_tuple()],'blind')
            associate_extracted_sources(last_img._id, deRuiter_r,
                                        new_source_sigma_margin)

            running_cat = columns_from_table(table="runningcatalog",
                                           keywords=['id', 'datapoints'],
                                           where={"dataset":self.dataset.id})
            self.assertEqual(len(running_cat), 1)
            self.assertEqual(running_cat[0]['datapoints'], img_idx+1)

            # Check runcat ID does not change for a steady single source
            if img_idx == 0:
                fixed_src_runcat_id = running_cat[0]['id']
                self.assertIsNotNone(fixed_src_runcat_id, "No runcat id assigned to source")
            self.assertEqual(running_cat[0]['id'], fixed_src_runcat_id,
                             "Multiple runcat ids for same fixed source")


            runcat_flux = columns_from_table(table="runningcatalog_flux",
                               keywords=['f_datapoints'],
                               where={"runcat":fixed_src_runcat_id})
            self.assertEqual(len(runcat_flux),1)
            self.assertEqual(img_idx+1, runcat_flux[0]['f_datapoints'])

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
                             msg="No entries in assocxtrsrcs for image number "+str(img_idx))
            self.assertEqual(assocxtrsrcs_rows[0]['runcat'], fixed_src_runcat_id,
                             "Mismatched runcat id in assocxtrsrc table")


