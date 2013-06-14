import unittest
import tempfile
import datetime
from tkp.conf.job_template import default_parset_paths
import tkp.utility.parset as parset
import StringIO
import ConfigParser


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
        parset.write_config_section(bufout, self.section, self.parset)
        bufin = StringIO.StringIO(bufout.getvalue())
        parsed = parset.read_config_section(bufin, self.section)
#        print parsed
        self.assertEqual(self.parset, parsed)


class TestAllSections(unittest.TestCase):
    def test_all_default_parsets(self):
        #This also demonstrates how we load everything into a single config
        master_config = ConfigParser.SafeConfigParser()
        master_config.read(default_parset_paths.values())
        for section in master_config.sections():
            section_params = parset.load_section(master_config, section)
    #        print "*********************************************"
    #        print "SECTION:", section
    #        print section_params
    #        print "*********************************************"
