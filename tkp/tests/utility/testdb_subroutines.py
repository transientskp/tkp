import os
from tkp.config import config as tkp_conf

#fresh_database_dump_filename = "fresh_db.sql"


def use_test_database_by_default():
    test_db_name = tkp_conf['test']['test_database_name']
    tkp_conf['database']['name'] = test_db_name
    tkp_conf['database']['user'] = test_db_name
    tkp_conf['database']['password'] = test_db_name     
    
#def prep_test_database():
#    if not tkp_conf['database']['enabled']:
#        raise ValueError("Database disabled in tkp config")
#    
#    if tkp_conf['test']['reset_test_database']:
#        #TO DO: Someone needs to figure out how to do this will database rollback on teardown!
#        #For now: Load database from dump file?
#        pass