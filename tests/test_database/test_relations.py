
import unittest
import datetime
import math

import tkp.database as tkpdb
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
        self.database.connection.rollback()
        #self.database.execute("delete from assocxtrsource")
        #self.database.execute("delete from runningcatalog_flux")
        #self.database.execute("delete from runningcatalog")
        self.database.close()

    def test_one2one(self):
        dataset = tkpdb.DataSet(database=self.database, data={'description': 'relation test set'})
        image_data = {'tau_time': 1, 'freq_eff': 10, 'freq_bw': 5, 'taustart_ts': datetime.datetime.now(), 'url': '/bla' }
        image = tkpdb.Image(data=image_data, dataset=dataset)

        ra = 33.3
        decl = 44.4
        x = math.cos(math.radians(decl))*math.cos(math.radians(ra))
        y = math.cos(math.radians(decl))*math.sin(math.radians(ra))
        z = math.sin(math.radians(decl))
        racosdecl = ra*math.cos(math.radians(decl))

        values = (str(ra), str(decl), "1", "2", "1", "2", "1", "2", "3", "4", "3", "2", str(image.id), "44", str(x), str(y), str(z), str(racosdecl))
        query = """\
        INSERT INTO extractedsource
          (ra
          ,decl
          ,ra_err
          ,decl_err
          ,f_peak
          ,f_peak_err
          ,f_int
          ,f_int_err
          ,det_sigma
          ,semimajor
          ,semiminor
          ,pa
          ,image
          ,zone
          ,x
          ,y
          ,z
          ,racosdecl
          )
        VALUES (
        """ + ",".join(values) + ")"


        self.database.execute(query)
        tkpdb.utils.associate_extracted_sources(self.database.connection, image.id)
