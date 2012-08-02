
import unittest
import datetime
import math

import tkp.database as tkpdb
import tkp.database.utils.general as dbgen
from ..decorators import requires_database


class TestSourceRelationAssociation(unittest.TestCase):
    """
    These tests will try all different combinations possible during source association
    """
    @requires_database()
    def setUp(self):

        self.database = tkpdb.DataBase()

    def tearDown(self):
        """remove all stuff after the test has been run"""
        #self.database.connection.rollback()
        #self.database.execute("delete from assocxtrsource")
        #self.database.execute("delete from runningcatalog_flux")
        #self.database.execute("delete from runningcatalog")
        self.database.close()

    def test_one2one(self):
        dataset = tkpdb.DataSet(database=self.database, data={'description': 'relation test set: 1-1'})
        
        # image 1
        image_data = {'tau_time': 1, 'freq_eff': 31000000, 'freq_bw': 2000000, 'taustart_ts': datetime.datetime.now(), 'url': '/bla' }
        image = tkpdb.Image(data=image_data, dataset=dataset, database=self.database)
        
        results = []
        # extractedsource 1
        ra, decl = 33.3, 44.4                       # degrees
        ra_err, decl_err = 1.5/3600., 2.0/3600.     # degrees (in db it will be converted to arcsec)
        f_peak, f_peak_err = 5.0, 0.1               # Jy
        f_int, f_int_err = 6.0, 0.15                # Jy
        det_sigma = 10.0                        
        semimajor, semiminor, pa = 1, 2, 3          # arcsec, arcsec, degrees
        src1 = [ra,decl,ra_err, decl_err, f_peak,f_peak_err, f_int,f_int_err,det_sigma,semimajor,semiminor, pa]
        results.append(src1)

        dbgen.insert_extracted_sources(self.database.connection, image.id, results)
        tkpdb.utils.associate_extracted_sources(self.database.connection, image.id)
