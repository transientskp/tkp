UPDATE version 
   SET value = 5
 WHERE name = 'revision'
   AND value = 6
;

ALTER TABLE extractedsource DROP COLUMN ra_fit_err;
ALTER TABLE extractedsource DROP COLUMN decl_fit_err;
ALTER TABLE extractedsource DROP COLUMN ra_sys_err;
ALTER TABLE extractedsource DROP COLUMN decl_sys_err;
