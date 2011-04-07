from __future__ import with_statement
import os
import tkp_lib.dataset as ds
import tkp_lib.database as db
from contextlib import closing

os.system('mysql -ulofar -pcs1 < /home/jds/Work/tkp-code/pipe/database/pipeline/MySQL/create.database.sql')
os.system('mysql -ulofar -pcs1 < /home/jds/Work/tkp-code/pipe/database/pipeline/MySQL/create.response.database.sql')
os.system('mysql -ulofar -pcs1 < /home/jds/Work/tkp-code/pipe/database/pipeline/MySQL/create.procedure.AssociateSource.sql')

my_ds = ds.DataSet('test', ('/home/jds/fits/corrected-all.fits',))

with closing(db.connection()) as con:
    with closing(con.cursor()) as cur:
        cur.callproc('InitObservation', (1,1))
    con.commit()
    my_ds[0].sextract().savetoDB(con)
    con.commit()
    

