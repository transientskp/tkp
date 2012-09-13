/*
RA 
04 04 00.0 +53 00 00, 4.52
02 56 3.79
01 48 22.67
00 40 2.22
23 32 2.06
22 34 4.14
21 16 2.21
20 08 14.1
19 00 4
17 52 10.72
16 44 
15 36
14 28
13 20
12 12 18.7
11 04
09 56
?? 8 48 8.6
07 40
06 32
?? 05 24
04 16
*/

DECLARE izoneheight, itheta DOUBLE;
DECLARE ira, idecl DOUBLE;

SET izoneheight = 1;
SET itheta = 1;

SET ira = ra2deg('01:48:00.00');
SET idecl = decl2deg('+53:00:00.00');

SELECT catsrcid
      ,orig_catsrcid
      ,ra
      ,decl
      ,ra2hms(ra)
      ,decl2dms(decl)
      ,i_int_avg
      ,i_int_avg_err
    FROM catalogedsources c1
   WHERE c1.cat_id = 4
     AND c1.x * COS(radians(idecl)) * COS(radians(ira)) 
         + c1.y * COS(radians(idecl)) * SIN(radians(ira))
         + c1.z * SIN(radians(idecl)) > COS(RADIANS(itheta))
     AND c1.zone BETWEEN CAST(FLOOR((idecl - itheta) / izoneheight) AS INTEGER)
                     AND CAST(FLOOR((idecl + itheta) / izoneheight) AS INTEGER)
     AND c1.ra BETWEEN ira - alpha(itheta, idecl)
                   AND ira + alpha(itheta, idecl)
     AND c1.decl BETWEEN idecl - itheta
                     AND idecl + itheta
ORDER BY i_int_avg
;

