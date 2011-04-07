#!/usr/bin/python

import os, time
import sys

starttime = time.time()

catdir = '/home/scheers/tkp-code/pipe/database/catfiles'

catfile = catdir + '/vlss/vlss-all.csv'
catfile_strip = catdir + '/vlss/vlss-all_strip.csv'

cat = open(catfile, 'r')
cat_strip = open(catfile_strip, 'w')

# A row in the original nvss cat file is defined as follows:
"""
#Column _RAJ2000    (F9.5)  Right ascension (FK5) Equinox=J2000. (computed by VizieR, not part of the original data)    [ucd=pos.eq.ra;meta.main]
#Column _DEJ2000    (F9.5)  Declination (FK5) Equinox=J2000. (computed by VizieR, not part of the original data)    [ucd=pos.eq.dec;meta.main]
#Column recno   (I8)    Record number within the original table (starting from 1)   [ucd=meta.record]
#Column VLSS    (a12)   VLSS name {\em(Name derived from truncated J2000 position; a suffix {\bf A} or {\bf B} was added in case of name collision)}    [ucd=meta.id;meta.main]
#Column RAJ2000 (A11)   Right Ascension J2000   [ucd=pos.eq.ra;meta.main]
#Column e_RAJ2000   (F5.2)  Mean error on RA    [ucd=stat.error;pos.eq.ra]
#Column DEJ2000 (A11)   Declination J2000   [ucd=pos.eq.dec;meta.main]
#Column e_DEJ2000   (F4.1)  Mean error on Declination   [ucd=stat.error;pos.eq.dec]
#Column Si  (F8.2)  Integrated flux density at 74MHz    [ucd=phot.flux.density;em.radio.20-100MHz]
#Column e_Si    (F7.2)  ? Mean error on Si (1)  [ucd=stat.error]
#Column l_MajAx (A1)    [<] Limit flag on MajAx [ucd=meta.code.error]
#Column MajAx   (F5.1)  Major axis of deconvolved component size    [ucd=phys.angSize]
#Column e_MajAx (F5.1)  ? Mean error on MajAx   [ucd=stat.error]
#Column l_MinAx (A1)    [<] Limit flag on MinAx [ucd=meta.code.error]
#Column MinAx   (F5.1)  Minor axis of deconvolved component size    [ucd=phys.angSize;src]
#Column e_MinAx (F4.1)  ? Mean error on MinAx   [ucd=stat.error]
#Column PA  (F6.2)  ? Position angle of Major Ax    [ucd=pos.posAng]
#Column e_PA    (F6.2)  ? Mean error on PA  [ucd=stat.error]
#Column Field   (a8)    Field designation (2)   [ucd=obs.field]
#Column Xpos    (I4)    X position of source on map [ucd=pos.cartesian.x;instr.det]
#Column Ypos    (I4)    Y position of source on map [ucd=pos.cartesian.y;instr.det]
#Column SPECFIND    (a8)    Show the spectrum of the source, on top of SPECFIND (Vollmer et al., Cat. VIII/74)  [ucd=meta.ref.url]

_RAJ2000;_DEJ2000;recno;VLSS;RAJ2000;e_RAJ2000;DEJ2000;e_DEJ2000;Si;e_Si;l_MajAx;MajAx;e_MajAx;l_MinAx;MinAx;e_MinAx;PA;e_PA;Field;Xpos;Ypos;SPECFIND
deg;deg;;;"h:m:s";s;"d:m:s";arcsec;Jy;Jy;;arcsec;arcsec;;arcsec;arcsec;deg;deg;;pix;pix;

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


