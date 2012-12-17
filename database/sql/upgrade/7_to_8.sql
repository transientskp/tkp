UPDATE version
   SET value = 8
 WHERE name = 'revision'
   AND value = 7
; %SPLIT%


INSERT INTO rejectreason VALUES (1, 'beam invalid'); %SPLIT%
INSERT INTO rejectreason VALUES (2, 'bright source near'); %SPLIT%