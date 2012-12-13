UPDATE version 
   SET value = 5
 WHERE name = 'revision'
; %SPLIT%

ALTER TABLE transient ADD COLUMN band SMALLINT DEFAULT 0; %SPLIT%
ALTER TABLE transient ADD COLUMN v_int DOUBLE; %SPLIT%
ALTER TABLE transient ADD COLUMN eta_int DOUBLE; %SPLIT%

UPDATE transient 
   SET v_int = v
      ,eta_int = eta
; %SPLIT%

ALTER TABLE transient DROP COLUMN v; %SPLIT%
ALTER TABLE transient DROP COLUMN eta; %SPLIT%

ALTER TABLE transient ADD FOREIGN KEY (band) REFERENCES frequencyband (id); %SPLIT%

