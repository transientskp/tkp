/*
COPY 
SELECT t.line
  FROM (
SELECT '# Region file format: DS9 version 4.0' AS rij 
 UNION 
SELECT 'fk5' AS rij
 UNION
SELECT 'box(2066.4872,1067.6551,0.14179903,0.03723213,359.99956) # color=cyan text={9}' AS rij
) t
INTO '/home/bscheers/maps/grb030329/regions/monetdb_test.reg' 
DELIMITERS ';'
          ,'\n' 
;
*/

COPY
SELECT t.line
  FROM (
SELECT '# Region file format: DS9 version 4.0' AS line 
 UNION 
SELECT '# Filename: /home/bscheers/maps/grb030329/fits/GRB030329_WSRT_20031225_1400.fits' AS line
 UNION 
SELECT 'global color=green font=\"helvetica 10 normal\" select=1 highlite=1 edit=1 move=1 delete=1 include=1 fixed=0 source' AS line
 UNION 
SELECT 'fk5' AS line
 UNION 
SELECT CONCAT('circle(', CONCAT(ra, CONCAT(',', CONCAT(decl, ',0.025) #color=yellow')))) AS line 
  FROM extractedsources 
 WHERE image_id = 1
       ) t
  INTO '/home/bscheers/maps/grb030329/regions/monetdb_test.reg' 
DELIMITERS ';'
          ,'\n'
          ,''
;

