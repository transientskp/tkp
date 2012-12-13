UPDATE version 
   SET value = 3 
 WHERE name = 'revision'
; %SPLIT%

DELETE FROM rejectreason WHERE id=0 and description='RMS too high'; %SPLIT%

