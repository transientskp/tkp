import unittest
import StringIO
import ConfigParser

import datetime
from tkp.testutil.data import default_parset_paths
import tkp.conf as conf


class TestParsingCode(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.section = 'test'
        cls.parset = {
               'float':0.5,
               'int':1,
               'string1':'bob',
               'string2':'0.235',
               'time':datetime.datetime.strptime('2007-07-20T14:18:09.909001', '%Y-%m-%dT%H:%M:%S.%f')
               }


    def test_round_trip(self):
        bufout = StringIO.StringIO()
        conf.write_config_section(bufout, self.section, self.parset)
        bufin = StringIO.StringIO(bufout.getvalue())
        parsed = conf.read_config_section(bufin, self.section)
#        print parsed
        self.assertEqual(self.parset, parsed)


class TestAllSections(unittest.TestCase):
    def test_all_default_parsets(self):
        #This also demonstrates how we load everything into a single config
        master_config = ConfigParser.SafeConfigParser()
        master_config.read(default_parset_paths.values())
        for section in master_config.sections():
            section_params = conf.parse_to_dict(master_config, section)
    #        print "*********************************************"
    #        print "SECTION:", section
    #        print section_params
    #        print "*********************************************"
