#!/usr/bin/python

import os, time
import sys

starttime = time.time()

catdir = '/home/scheers/tkp-code/pipe/database/catfiles'

catfile = catdir + '/wenss/wenss-all.csv'
catfile_strip = catdir + '/wenss/wenss-all_strip.csv'

cat = open(catfile, 'r')
cat_strip = open(catfile_strip, 'w')

# A row in the original nvss cat file is defined as follows:
"""
#Column _RAJ2000    (F9.5)  Right ascension (FK5) Equinox=J2000. (computed by VizieR, not part of the original data)    [ucd=pos.eq.ra;meta.main]
#Column _DEJ2000    (F9.5)  Declination (FK5) Equinox=J2000. (computed by VizieR, not part of the original data)    [ucd=pos.eq.dec;meta.main]
#Column recno   (I8)    Record number within the original table (starting from 1)   [ucd=meta.record]
#Column Name    (a13)   Designation of the source   [ucd=meta.id;meta.main]
#Column f_Name  (A1)    [abmp] Several objects share the same name  [ucd=meta.code.error]
#Column RA1950  (A11)   Right Ascension B1950 (hours)   [ucd=pos.eq.ra;meta.main]
#Column DE1950  (A11)   Declination B1950 (degrees) [ucd=pos.eq.dec;meta.main]
#Column RAJ2000 (A11)   Right Ascension J2000 (hours)   [ucd=pos.eq.ra;meta.main]
#Column DEJ2000 (A11)   Declination J2000 (degrees) [ucd=pos.eq.dec;meta.main]
#Column flg1    (A1)    [SMEC] source type flag [ucd=meta.code]
#Column flg2    (A1)    [*] problems in fitting the source  [ucd=meta.code]
#Column Speak   (I6)    Peak flux density at 330MHz in mJy/beam [ucd=phot.flux.density;em.radio.200-400MHz]
#Column Sint    (I7)    Integrated flux density 330MHz in mJy   [ucd=phot.flux.density;em.radio.200-400MHz]
#Column MajAxis (I4)    Major axis  [ucd=phys.angSize;src]
#Column MinAxis (I3)    Minor axis  [ucd=phys.angSize;src]
#Column PA  (I3)    Position angle (North to East)  [ucd=pos.posAng]
#Column Nse (F4.1)  Local rms-noise level in mJy/beam   [ucd=instr.skyLevel]
#Column Frame   (a9)    Frame from which the source was obtained    [ucd=obs.field]

_RAJ2000;_DEJ2000;recno;Name;f_Name;RA1950;DE1950;RAJ2000;DEJ2000;flg1;flg2;Speak;Sint;MajAxis;MinAxis;PA;Nse;Frame
deg;deg;;;;"h:m:s";"d:m:s";"h:m:s";"d:m:s";;;mJy;mJy;arcsec;arcsec;deg;mJy;

"""

row = 0
for line in cat:
    row += 1
    rw = line.split(';')
    r = ''
    w = ''
    for i in range(len(rw)):
        r = r + rw[i] + ';'
        if i < len(rw) - 1:
            w = w + rw[i].strip() + ';'
        else:
            w = w + rw[i].strip() + '\n'
    #print row, ':', w
    cat_strip.write(w)
cat.close()
cat_strip.close()

print row, 'lines written to file', catfile_strip


