import unittest
if not  hasattr(unittest.TestCase, 'assertIsInstance'):
    import unittest2 as unittest
import tkp.database as tkpdb
import tkp.database.utils as dbutils
import tkp.config
import tests.db_subs as db_subs
from tests.decorators import requires_database

@unittest.skipIf(not eval(tkp.config.config['test']['long']), "not runnig prolonged test suite")
class TestTransientCandidateMonitoring(unittest.TestCase):
    @requires_database()
    def setUp(self):
        self.database = tkpdb.DataBase()
        self.dataset = tkpdb.DataSet(data={'description':"Mon:"+self._testMethodName},
                                    database = self.database)

        self.n_images = 8                
        self.im_params = db_subs.example_dbimage_datasets(self.n_images)
        self.db_imgs=[]

        source_lists=db_subs.example_source_lists(n_images=8,
                                                  include_non_detections=False)
                
        for i in xrange(self.n_images):
            self.db_imgs.append(
                        tkpdb.Image(data=self.im_params[i], 
                                            dataset=self.dataset)
                                )
            self.db_imgs[i].insert_extracted_sources(source_lists[i])
            self.db_imgs[i].associate_extracted_sources(deRuiter_r=3.7)
            
        fixed_src_rc_entries = dbutils.columns_from_table(
                                           self.database.connection, 
                                           'runningcatalog',
                                           ['id'],
                                           alias={'id':'runcat'},
                                           where={'dataset':self.dataset.id,
                                                  'datapoints': self.n_images}
                                                     )
        self.fixed_src_runcatids = [i['runcat'] for i in fixed_src_rc_entries]
#        print "Fixed src RCID:", self.fixed_src_runcatid 
        
            
    def tearDown(self):
        self.database.close()

    def test_winkers(self):
        """test_winkers
        --- Tests the SQL call which finds sources not present in all epochs
        """
        
        winkers = tkpdb.utils.select_winking_sources(
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
        winkers = tkpdb.utils.select_winking_sources(
                   self.database.connection,
                   self.dataset.id)
        
        all_results = tkpdb.utils.select_transient_candidates_above_thresh(
                    self.database.connection, 
                    [c['runcat'] for c in winkers],
                    0,
                    0)
        self.assertEqual(len(winkers), len(all_results))
        
        bright_results = tkpdb.utils.select_transient_candidates_above_thresh(
                    self.database.connection, 
                    [c['runcat'] for c in winkers],
                    10,
                    10)
        self.assertEqual(len(bright_results), 1)
        self.assertEqual(bright_results[0]['max_det_sigma'], 15)
        
        #Should return bright single epoch, and fainter two epoch sources
        solid_results = tkpdb.utils.select_transient_candidates_above_thresh(
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
    
    def test_blind_source_insertion(self):
        """test_blind_source_insertion
        
        Check that the insertion really is idempotent, 
        i.e. checks for runcat ids before insertion.
        """
        runcat_entries = self.dataset.runcat_entries()
        tkpdb.utils.add_runcat_sources_to_monitoringlist(
                        self.database.connection,
                        self.dataset.id, 
                        [runcat_entries[-1]['runcat']])

        mon_entries = self.db_imgs[-1].monitoringsources()
        self.assertEqual(len(mon_entries), 1)
        
        #Again to check non-duplication
        tkpdb.utils.add_runcat_sources_to_monitoringlist(
                self.database.connection,
                self.dataset.id, 
                [runcat_entries[-1]['runcat']])

        mon_entries = self.db_imgs[-1].monitoringsources()
        self.assertEqual(len(mon_entries), 1)
            
        
        
        
        
    def test_blind_source_insertion_and_retrieval(self):
        """test_blind_source_insertion_and_retrieval

            We have faked transient sources for imgs
            3,4,5 and 6.
            
            In total we have 3 different fake transients.
            
            Therefore we should monitor all 3 in the imgs with
            only an extraction from the fixed source. 
        """
        self.dataset.mark_transient_candidates(0, 0)
        for dbimg in self.db_imgs[0:3]:
            srcs_to_monitor = dbimg.monitoringsources()
            self.assertEqual(len(srcs_to_monitor),3)
            
            retrieved_mon_rc_ids = [src.runcat for src in srcs_to_monitor]
            all_runcat_ids = [i['runcat'] for i in self.dataset.runcat_entries()]
            known_mon_rcids = set(all_runcat_ids).difference(set(self.fixed_src_runcatids))
            self.assertEqual(set(retrieved_mon_rc_ids),known_mon_rcids )
            
                 
                
        for dbimg in self.db_imgs[3:7]:
            srcs_to_monitor = dbimg.monitoringsources()
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
        runcat_entries = self.dataset.runcat_entries()
#        print "Runcat rows:", runcat_rows
        self.assertEqual(len(runcat_entries), 4)
        
        """
        Count the number of extracted sources associated with a given xtrsrc_id
        
        Args: A list of xtrsrc_ids to process.
        
        Returns: A list of pairwise tuples,
        [ (assoc_src_id, assocs_count) ]
        
        """
        src_ids = [r['xtrsrc'] for r in runcat_entries]
        try:
            #Thought about trying to do this in one clever SQL statement
            #But this will have to do for now.
            
            #First, get the runcat ids for these extracted sources
            ids_placeholder = ", ".join(["%s"] * len(src_ids))
            query="""\
SELECT runcat
FROM assocxtrsource
WHERE xtrsrc in ({0})
""".format(ids_placeholder)
            self.database.cursor.execute(query, tuple(src_ids))
            runcat_ids = self.database.cursor.fetchall()
            
            #Then count the associations
            query="""\
SELECT runcat, count(xtrsrc)
FROM assocxtrsource
WHERE runcat in ({0})
GROUP BY runcat
""".format(ids_placeholder)
            self.database.cursor.execute(query, tuple(i[0] for i in runcat_ids))
            id_counts = self.database.cursor.fetchall()
        except db.Error:
            logging.warn("Failed on query %s", query)
            raise
        finally:
            self.database.cursor.close()
        
        assoc_counts = id_counts
        #assoc_counts = tkpdb.utils.count_associated_sources(self.database.connection,
        #                           [r['xtrsrc'] for r in runcat_entries])
        for count in assoc_counts:
            self.assertEqual(count[1], 8)
#        print "Assoc counts:", assoc_counts
        
        
    def test_manual_insertion(self):
        """test_manual_insertion
        
            Check that manually entered entries are dealt with correctly
        """
        test_coords = (123.999,15.999)
        self.dataset.add_manual_entry_to_monitoringlist(ra = test_coords[0],
                                                        dec = test_coords[1])
#        tkpdb.utils.add_manual_entry_to_monitoringlist(
#                       self.database.connection,
#                       self.dataset.id, 
#                       )
#        print "DSID:", self.dataset.id
        for dbimg in self.db_imgs:
            manual_srcs = tkpdb.utils.get_monitoringlist_not_observed_manual_entries(
                             self.database.connection,
                             dbimg.id,
                             self.dataset.id)
            self.assertEqual(len(manual_srcs), 1)
            all_srcs_to_monitor = dbimg.monitoringsources()
            self.assertEqual(len(manual_srcs), len(all_srcs_to_monitor))
            self.assertEqual(all_srcs_to_monitor[0].runcat,None)
            self.assertAlmostEqual(all_srcs_to_monitor[0].ra,test_coords[0])
            self.assertAlmostEqual(all_srcs_to_monitor[0].decl,test_coords[1])
#            print "Monitor:", all_srcs_to_monitor

    def test_mixed_retrieval(self):
        """test_mixed_retrieval
        Tests a combination of user and automated entries to the monitoringlist
        """
        self.dataset.add_manual_entry_to_monitoringlist(ra = 123.999,
                                                        dec = 15.999)
        self.dataset.mark_transient_candidates(0, 0)
        for dbimg in self.db_imgs[0:3]:
            srcs_to_monitor = dbimg.monitoringsources() 
            self.assertEqual(len(srcs_to_monitor),3+1)
            
        for dbimg in self.db_imgs[3:7]:
            srcs_to_monitor = dbimg.monitoringsources()
            self.assertEqual(len(srcs_to_monitor),2+1)
        
        
