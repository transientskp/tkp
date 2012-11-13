UPDATE version 
   SET value = 3 
 WHERE name = 'revision'
;

DELETE FROM rejectreason WHERE id=0 and description='RMS too high';

--ALTER TABLE transient DROP FOREIGN KEY (band) REFERENCES frequencyband (id);
ALTER TABLE transient DROP CONSTRAINT "transient_band_fkey";

ALTER TABLE transient ADD COLUMN v DOUBLE;
ALTER TABLE transient ADD COLUMN eta DOUBLE;

UPDATE transient 
   SET v = v_int
      ,eta = eta_int
;

ALTER TABLE transient DROP COLUMN v_int;
ALTER TABLE transient DROP COLUMN eta_int;
ALTER TABLE transient DROP COLUMN band;

