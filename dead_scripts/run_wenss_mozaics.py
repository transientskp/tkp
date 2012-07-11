#!/usr/bin/python

import os, time
import tkp_lib.database as db
import tkp_lib.dataset as d
import tkp_lib.settings as s
from tkp_lib import image, accessors, containers, coordinates

starttime = time.time()

basedir = '/home/bscheers/maps/wenss/mozaics/'
#basedir = '/home/bscheers/maps/wenss/'
imagesdir = basedir + 'fits/'

logtime = time.strftime("%Y-%m-%d-%H:%M:%S")
logfile = basedir + 'log/proctimes' + logtime + '.log'
#log = open(logfile, 'w')
#row = 'image; ' + 'nsources; ' + 'subtotal; ' + 'dbelapsed; ' + 'imgelapsed; \n'
#log.write(row)
#row = '------------------------------------------------------ \n'
#log.write(row)

#dataset = d.DataSet('Testing pipeline_test database; WENSS det=7', images)
dataset = d.DataSet('Testing WENSS MOZAICS 6 NIGHTS: 66.083.I')
#print dataset
#print "dataset id: ", dataset.id

conn = db.connection()
#print conn

i = 0
files = os.listdir(imagesdir)
files.sort()
for file in files:
    #if (file == '66.083.I.NIGHT4.FITS'):
    #if (file == 'WN55074H'):
        print "i: ", i
        #dataset.append(imagesdir + file)
        imgstarttime = time.time()
        my_fitsfile = accessors.FitsFile(imagesdir + file)
        my_image = image.ImageData(my_fitsfile, dataset = dataset)
        my_image.wcs.coordsys  = 'fk4' 
        my_image.wcs.outputsys = 'fk4'
        #results = my_image.extract(det=20)
        cursor = conn.cursor()
        #373 sources:
        # orig_catsrcid <> 49964 gave troouble in multiple assocs (this will be taken care of)
        query = "select ra,decl from cataloguedsources where cat_id = 3 and zone between 62 and 68 and ra between 82 and 88 and right(rtrim(catsrcname),1) <> 'B' and right(rtrim(catsrcname),1) <> 'A';"
        #query = "select ra,decl from cataloguedsources where cat_id = 3 and zone between 46 and 55 and ra between 67 and 80 and i_peak_avg > 0.1;"
        cursor.execute(query)
        rows = cursor.fetchall()
        k = 0
        for row in rows:
            print "k: ", k
            spatialpos = [row[0], row[1]]
            print spatialpos
            k = k + 1
            pixpos = my_image.wcs.s2p(spatialpos)
            print pixpos
            detection = my_image.fit_to_point(pixpos[0], pixpos[1], 10, threshold=-10., fixed='position')
            print detection.serialize()
            dbstarttime = time.time()
            cursor.callproc('AssocSrc', detection.serialize())
            dbendtime = time.time()
            dbelapsed = dbendtime - dbstarttime
            #cursor.close()
            conn.commit()
            imgendtime = time.time()
            #nsources = len(results)
            nsources = 1
            imgelapsed = imgendtime - imgstarttime
            print "Image processing time %6.3f seconds" % (imgelapsed)
            #results.savetoDB(conn)
            print "DB insertion time %6.3f seconds" % (dbelapsed)
            subtotelapsed = dbelapsed + imgelapsed
            #print "Subtotal proc time %6.3f seconds" % (subtotelapsed)
            #row = str(i) + ';' + str(nsources) + ';' + str(subtotelapsed) + ';' + str(dbelapsed) + ';' + str(imgelapsed) + '\n'
            #log.write(row)
        cursor.close()
        my_image.clearcache()
        i = i + 1

endtime = time.time()
elapsed = endtime - starttime

#log.close()
conn.close()

print "Total processing time %.3f seconds" % (elapsed)

