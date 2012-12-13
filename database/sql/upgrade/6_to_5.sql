UPDATE version 
   SET value = 5
 WHERE name = 'revision'
   AND value = 6
; %SPLIT%

ALTER TABLE extractedsource DROP COLUMN ra_fit_err; %SPLIT%
ALTER TABLE extractedsource DROP COLUMN decl_fit_err; %SPLIT%
ALTER TABLE extractedsource DROP COLUMN ra_sys_err; %SPLIT%
ALTER TABLE extractedsource DROP COLUMN decl_sys_err; %SPLIT%
