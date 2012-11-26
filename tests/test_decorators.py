import unittest
if not  hasattr(unittest.TestCase, 'assertIsInstance'):
    import unittest2 as unittest
import tkp.config
import os
from tkp.testutil.decorators import requires_database, requires_data, duration

def debug_print(*args):
    return #Comment to switch on debug prints.
    print "**",
    for a in args:
        print a,
    print "**"


class TestDatabaseDecorators(unittest.TestCase):
    @requires_database()
    def test_requires_database(self):
        debug_print( "Database testing enabled.")
        
        
class TestDataDecorators(unittest.TestCase):
    def test_datapath_defined(self):
        self.assertNotEqual(tkp.config.config['test']['datapath'], None )
        debug_print( "Test data path:", 
                     tkp.config.config['test']['datapath'])
        
    @requires_data(os.path.join(tkp.config.config['test']['datapath'], 
                                'CORRELATED_NOISE.FITS'))
    def test_requires_data_decorator(self):
        f = open(os.path.join(tkp.config.config['test']['datapath'], 
                              'CORRELATED_NOISE.FITS'))
        
    
class TestDurationDecorator(unittest.TestCase):
    def test_max_duration_defined(self):
        debug_print("Max_duration:", tkp.config.config['test']['max_duration'])
        debug_print("Max_duration type:", 
                    type(tkp.config.config['test']['max_duration']))
        
    @duration(5)
    def test_short(self):
        debug_print("Will run test duration = 5") 
    @duration(25)
    def test_medium(self):
        debug_print("Will run test duration = 25")
    @duration(300)
    def test_long(self):
        debug_print("Will run test duration = 300")
        
            
            