# Region file format: DS9 version 4.0
# Filename: /scratch/bscheers/databases/maps/wenss/fits/WN30224H
global color=green font="helvetica 10 normal" select=1 highlite=1 edit=1 move=1 delete=1 include=1 fixed=0 source
fk5

SELECT CONCAT('circle(', ra, ',', decl, ',0.025) #color=yellow') FROM associatedsources,extractedsources WHERE xtrsrcid = assoc_xtrsrcid AND xtrsrc_id <> assoc_xtrsrcid ;



SELECT '# Region file format: DS9 version 4.0 \n'
      ,'# Filename: /scratch/bscheers/databases/maps/wenss/fits/WN30224H \n'
      ,'global color=green font="helvetica 10 normal" select=1 highlite=1 edit=1 move=1 delete=1 include=1 fixed=0 source \n'
      ,'fk5 \n'
      ,CONCAT('circle(', ra, ',', decl, ',0.025) #color=yellow')
  INTO OUTFILE '/home/bscheers/maps/wenss/regions/this.reg'
FIELDS TERMINATED BY ';' 
LINES TERMINATED BY '\n'
  FROM associatedsources
      ,extractedsources 
 WHERE xtrsrcid = assoc_xtrsrcid 
   AND xtrsrc_id <> assoc_xtrsrcid 
;
