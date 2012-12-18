UPDATE version 
   SET value = 7
 WHERE name = 'revision'
   AND value = 8
; %SPLIT%

ALTER TABLE image DROP COLUMN rejected; %SPLIT%

