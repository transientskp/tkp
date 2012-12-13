UPDATE version 
   SET value = 6
 WHERE name = 'revision'
   AND value = 5
;

ALTER TABLE extractedsource ADD COLUMN ra_fit_err DOUBLE NULL;
ALTER TABLE extractedsource ADD COLUMN decl_fit_err DOUBLE NULL;
ALTER TABLE extractedsource ADD COLUMN ra_sys_err DOUBLE NULL;
ALTER TABLE extractedsource ADD COLUMN decl_sys_err DOUBLE NULL;

UPDATE extractedsource
   SET ra_fit_err = ra_err
      ,decl_fit_err = decl_err
      ,ra_sys_err = 0
      ,decl_sys_err = 0
;

ALTER TABLE extractedsource ALTER COLUMN ra_fit_err SET NOT NULL;
ALTER TABLE extractedsource ALTER COLUMN decl_fit_err SET NOT NULL;
ALTER TABLE extractedsource ALTER COLUMN ra_sys_err SET NOT NULL;
ALTER TABLE extractedsource ALTER COLUMN decl_sys_err SET NOT NULL;
