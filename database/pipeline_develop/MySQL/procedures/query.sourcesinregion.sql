SELECT '# Region file format: DS9 version 4.0' 
 UNION 
SELECT '# Filename: /home/bscheers/maps/grb030329/fits/GRB030329_WSRT_20031225_1400.fits' 
 UNION 
SELECT 'global color=green font="helvetica 10 normal" select=1 highlite=1 edit=1 move=1 delete=1 include=1 fixed=0 source' 
 UNION 
SELECT 'fk5' 
 UNION 
SELECT CONCAT('circle(', ra, ',', decl, ',0.025) #color=red, text={',xtrsrcid,'}') 
  INTO OUTFILE '/home/bscheers/maps/grb030329/regions/textincl.reg' 
FIELDS TERMINATED BY ';' 
LINES TERMINATED BY '\n' 
  FROM extractedsources 
 WHERE image_id = 1
;
