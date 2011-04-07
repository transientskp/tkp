import os
import tkp_lib.dbregion as rg
import tkp_lib.database as db
conn=db.connection()

#outpath = '/home/bscheers/simsa/posflux/regions10/'
outpath = os.getenv('HOME') + '/maps/grb030329/pbcor/regions/'
#imageid=[192,193,195]
#imageid = [1337,1338,1339,1340,1343,1344,1347,1348,1349,1350,1351,1353,1363]
#imageid = [83,84,85,86,87,88,89,90,]
#clr = ['red','red','red','red','red','red','yellow','yellow','yellow','yellow','yellow','yellow','magenta']
#for i in range(len(imageid)):
rg.createRegionByImage(84,conn,outpath, 'magenta')

