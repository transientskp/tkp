UPDATE version
   SET value = 7
 WHERE name = 'revision'
   AND value = 8
; %SPLIT%

DELETE FROM rejectreason WHERE id=1; %SPLIT%
DELETE FROM rejectreason WHERE id=2; %SPLIT%
