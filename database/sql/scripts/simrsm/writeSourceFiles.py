import os
import sys

NsourcesIn=int(sys.argv[1])
NsourcesOut=int(sys.argv[2])

path = os.getenv('HOME') + '/tkp-code/pipe/database/pipeline_develop/MonetDB/scripts/simrsm'

infile = path + '/copy.into.extractedsources.' + str(NsourcesIn) + '.csv'
outfile = path + '/copy.into.extractedsources.' + str(NsourcesOut) + '.csv'

fi = open(infile,'r')
fo = open(outfile,'w')

dra = 1.
ddecl = 2.
for line in fi:
    #print line
    #for i in range(5):
    for i in range(10):
        #ra0 = float(line.split(',')[1])
        decl0 = float(line.split(',')[2])
        #ra_p = ra0 + (i+1) * dra
        #ra_m = ra0 - i * dra
        decl_p = decl0 + i * dra
        row_p=''
        #row_m=''
        for col in range(len(line.split(','))):
            if col == 2:
                #row_p += str(ra_p) + ','
                #row_m += str(ra_m) + ','
                row_p += str(decl_p) + ','
            else:
                if col == len(line.split(',')) - 1:
                    row_p += line.split(',')[col] 
                    #row_m += line.split(',')[col] 
                else:
                    row_p += line.split(',')[col] + ','
                    #row_m += line.split(',')[col] + ','
        #print "row_p = ", row_p
        #print "row_m = ", row_m
        fo.write(row_p)
        #fo.write(row_m)

fi.close()
fo.close()

print "File ", outfile, " written"

