UPDATE version 
   SET value = 4 
 WHERE name = 'revision'
; %SPLIT%

--ALTER TABLE transient DROP FOREIGN KEY (band) REFERENCES frequencyband (id);
ALTER TABLE transient DROP CONSTRAINT "transient_band_fkey"; %SPLIT%

ALTER TABLE transient ADD COLUMN v DOUBLE; %SPLIT%
ALTER TABLE transient ADD COLUMN eta DOUBLE; %SPLIT%

UPDATE transient 
   SET v = v_int
      ,eta = eta_int
; %SPLIT%

ALTER TABLE transient DROP COLUMN v_int; %SPLIT%
ALTER TABLE transient DROP COLUMN eta_int; %SPLIT%
ALTER TABLE transient DROP COLUMN band; %SPLIT%

