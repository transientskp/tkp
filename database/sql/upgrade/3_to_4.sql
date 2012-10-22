UPDATE version 
   SET value = 4 
 WHERE name = 'revision'
;

ALTER TABLE transient ADD COLUMN band SMALLINT DEFAULT 0;
ALTER TABLE transient ADD COLUMN v_int DOUBLE;
ALTER TABLE transient ADD COLUMN eta_int DOUBLE;

UPDATE transient 
   SET v_int = v
      ,eta_int = eta
;

ALTER TABLE transient DROP COLUMN v;
ALTER TABLE transient DROP COLUMN eta;

ALTER TABLE transient ADD FOREIGN KEY (band) REFERENCES frequencyband (id);

