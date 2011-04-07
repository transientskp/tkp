#!/usr/bin/python

import os, time
import sys

starttime = time.time()

catdir = '/home/scheers/tkp-code/pipe/database/catfiles'

catfile = catdir + '/nvss/nvss-all.csv'
catfile_strip = catdir + '/nvss/nvss-all_strip.csv'

cat = open(catfile, 'r')
cat_strip = open(catfile_strip, 'w')

# A row in the original nvss cat file is defined as follows:
"""
olumn _RAJ2000    (F9.5)  Right ascension (FK5) Equinox=J2000. (computed by VizieR, not part of the original data)    [ucd=pos.eq.ra;meta.main]
#Column _DEJ2000    (F9.5)  Declination (FK5) Equinox=J2000. (computed by VizieR, not part of the original data)    [ucd=pos.eq.dec;meta.main]
#Column recno   (I8)    Record number within the original table (starting from 1)   [ucd=meta.record]
#Column Field   (a8)    Name of the original survey image field from which the component was derived.   [ucd=obs.field]
#Column Xpos    (F7.2)  X position (RA direction) of the radio source   [ucd=pos.cartesian.x;instr.det]
#Column Ypos    (F7.2)  Y position (Dec direction) of the radio source  [ucd=pos.cartesian.y;instr.det]
#Column NVSS    (a14)   Source name (1) [ucd=meta.id;meta.main]
#Column RAJ2000 (A11)   Right Ascension J2000 (2)   [ucd=pos.eq.ra;meta.main]
#Column DEJ2000 (A11)   Declination J2000 (2)   [ucd=pos.eq.dec;meta.main]
#Column e_RAJ2000   (F5.2)  Mean error on RA    [ucd=stat.error;pos.eq.ra]
#Column e_DEJ2000   (F4.1)  Mean error on Dec   [ucd=stat.error;pos.eq.dec]
#Column S1.4    (F8.1)  Integrated 1.4GHz flux density of radio source  [ucd=phot.flux.density;em.radio.750-1500MHz]
#Column e_S1.4  (F7.1)  Mean error on S1.4  [ucd=stat.error]
#Column l_MajAxis   (A1)    Limit flag on MajAxis   [ucd=meta.code.error;phys.angSize]
#Column MajAxis (F5.1)  Fitted (deconvolved) major axis of radio source [ucd=phys.angSize;em.radio;meta.modelled]
#Column l_MinAxis   (A1)    Limit flag on MinAxis   [ucd=meta.code.error;phys.angSize]
#Column MinAxis (F5.1)  Fitted (deconvolved) minor axis of radio source [ucd=phys.angSize;em.radio;meta.modelled]
#Column PA  (F5.1)  [-90, 90]? Position angle of fitted major axis  [ucd=pos.posAng;meta.modelled]
#Column e_MajAxis   (F4.1)  ? Mean error on MajAxis [ucd=stat.error;phys.angSize]
#Column e_MinAxis   (F4.1)  ? Mean error on MinAxis [ucd=stat.error;phys.angSize]
#Column e_PA    (F4.1)  ? Mean error on PA  [ucd=stat.error]
#Column f_resFlux   (A2)    [PS* ] Residual Code (3)    [ucd=meta.code]
#Column resFlux (I4)    ? Peak residual flux, in mJy/beam (3)   [ucd=phot.flux.density;em.radio]
#Column polFlux (F6.2)  ? Integrated linearly polarized flux density    [ucd=phot.flux.density]
#Column polPA   (F5.1)  [-90,90]? The position angle of polFlux (4) [ucd=pos.posAng;phys.polarization]
#Column e_polFlux   (F5.2)  ? Mean error on polFlux [ucd=stat.error]
#Column e_polPA (F4.1)  ? Mean error on polPA   [ucd=stat.error]
#Column Image   (a5)    FITS Image of the target, about 200x200 pixels of 5x5arcsec (or consult http://www.cv.nrao.edu/nvss/postage.shtml)  [ucd=meta.ref.url]

_RAJ2000;_DEJ2000;recno;Field;Xpos;Ypos;NVSS;RAJ2000;DEJ2000;e_RAJ2000;e_DEJ2000;S1.4;e_S1.4;l_MajAxis;MajAxis;l_MinAxis;MinAxis;PA;e_MajAxis;e_MinAxis;e_PA;f_resFlux;resFlux;polFlux;polPA;e_polFlux;e_polPA;Image
deg;deg;;;pix;pix;;"h:m:s";"d:m:s";s;arcsec;mJy;mJy;;arcsec;;arcsec;deg;arcsec;arcsec;deg;;mJy;mJy;deg;mJy;deg;
---------;---------;--------;--------;-------;-------;--------------;-----------;-----------;-----;----;--------;-------;-;-----;-;-----;-----;----;----;---

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


