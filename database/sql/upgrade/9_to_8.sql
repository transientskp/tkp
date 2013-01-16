UPDATE version 
   SET value = 8
 WHERE name = 'revision'
   AND value = 9
; %SPLIT%

ALTER TABLE image DROP COLUMN rejected; %SPLIT%
