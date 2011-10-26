"""

Module that checks the database for source associations


If the database is not available or the database module cannot be
imported, functions will silently return None.
"""


import_failed = False
try:
    from tkp.database.database import DataBase
    from tkp.database.utils import match_nearest_in_catalogs
    
except ImportError:
    import_failed = True

def match_catalogs(transient):
    if import_failed:
        return None
    # Hardcode the catalogs for now
    catalogs = {3: 'NVSS', 4: 'VLSS', 5: 'WENSS', 6: 'WENSS'} 
    database = DataBase()
    results = {}
    for key, value in catalogs.iteritems():
        results[value] = match_nearest_in_catalogs(
            database.connection, transient.srcid,
            radius=1, catalogid=key, assoc_r=.1)
        if len(results[value]) > 0:
            results[value] = results[value][0]
        else:
            results[value] = {}
    return results

            
