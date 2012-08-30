"""
A quick and dirty example of how to use TKP-DB interface.

The aim of this script is to gather the std. dev. in RA,DEC 
for the sources in a dataset.

We filter to only grab the sources which appear in every image,
to exclude noisy sources.

NB The script is pretty damn inefficient and could easily 
be replaced using some custom SQL queries, (probably 2 or 3 max)
but the aim is to initiate new users without teaching them SQL...

-TS 02/08/12
""" 


import tkp.database as tkpdb
import tkp.database.utils as dbutils

import numpy


def main(argv):
    
    my_db_name = 'testdb' #Your monetdb database
    db = tkpdb.DataBase(name=my_db_name, user=my_db_name, password=my_db_name)

    #EITHER:
    #Use most recently entered dataset 
    #ds_id =  get_most_recent_dataset(db.connection)
    #Or: specify the id after looking it up in the TKP-WEB pages:
    ds_id = 52
    
    dataset = tkpdb.DataSet(id=ds_id, database=db)
    print "Dataset name:", dataset._data['description']
    dataset.update_images()
    n_images = len(dataset.images)
    print "Contains", n_images, 'images'
    
    #Get the assocatiation ids (`running catalog' ids)
    runcat_info = dataset.runcat_entries()
    
    print "Runcat entries:"
    print runcat_info
    
    rc_ids= [entry['runcat'] for entry in runcat_info]
    
    selected_sources_info=[]
    for rc_id in rc_ids:
        ##Only pull the sources which appear in all the images
        ##This might only leave a few though?
        ## And obviously will favour bright sources.
        if entry['datapoints'] == n_images:
            selected_sources_info.append(
                     gather_source_info(rc_id,
                                        db.connection)
                     )

    print "Srcs info:"
    print selected_sources_info
    return 0

def get_most_recent_dataset(conn):
    dsid_dicts = dbutils.columns_from_table(conn,
                               table='dataset',
                               keywords=['id'],
                               alias={'id':'datasetid'},
                               where=None)
    return dsid_dicts[-1]['datasetid']

def gather_source_info(runcatid, conn):
    """
    Pulls information from extracted sources which have 
    been marked as associated together, and tagged with this 
    running catalog id.
    
    Returns: A tuple,
        ( ra_std_dev, dec_std_dev)
    
    Logic:
    -Grab all the xtrsrc ids associated with this runcatid
    -Get the corresponding entries from extractedsource
    -Calculate std. deviation etc.
    """    
    
    assocxtrsrc_entries = dbutils.columns_from_table(conn,
                         table='assocxtrsource',
                         keywords = ['xtrsrc'],
                         where = {'runcat': runcatid}
                         )
    xtrsrc_ids = [entry['xtrsrc'] for entry in assocxtrsrc_entries]
    extractedsources=[]
    
    #This bit in particular is horribly horribly inefficient,
    # as it stands. Oh well.
    for id in xtrsrc_ids:
        extractedsources.extend(
            dbutils.columns_from_table(conn,
                   table='extractedsource',
                   where={'id':id}
                   )
                                )
    
#    print "Extracted sources:"
#    for src in extractedsources:
#        print src
    
    ra_list = [src['ra'] for src in extractedsources]
    dec_list = [src['decl'] for src in extractedsources]
    
    src_info = {'runcat':runcatid,
                'ra': numpy.mean(ra_list),
                'dec': numpy.mean(dec_list),
                'ra_sd':numpy.std(ra_list), 
                'dec_sd':numpy.std(dec_list)
                }
    return  src_info

if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv))
    
    