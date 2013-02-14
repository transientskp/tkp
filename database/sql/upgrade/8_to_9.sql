UPDATE version
   SET value = 9
 WHERE name = 'revision'
   AND value = 8
; %SPLIT%

CREATE SEQUENCE seq_skyregion AS INTEGER; %SPLIT%
CREATE TABLE skyregion 
  (id INTEGER NOT NULL DEFAULT NEXT VALUE FOR seq_skyregion
  ,dataset INTEGER NOT NULL
  ,centre_ra DOUBLE NOT NULL
  ,centre_decl DOUBLE NOT NULL
  ,xtr_radius DOUBLE NOT NULL
  ,x DOUBLE NOT NULL
  ,y DOUBLE NOT NULL
  ,z DOUBLE NOT NULL
  ,PRIMARY KEY (id)
  ,FOREIGN KEY (dataset) REFERENCES dataset (id)
  )
;
%SPLIT%

CREATE TABLE assocskyrgn
  (runcat INT NOT NULL
  ,skyrgn INT NOT NULL
  ,distance_deg DOUBLE 
  ,FOREIGN KEY (runcat) REFERENCES runningcatalog (id)
  ,FOREIGN KEY (skyrgn) REFERENCES skyregion (id)
);
%SPLIT%


DROP FUNCTION insertImage; %SPLIT%

ALTER TABLE IMAGE ADD COLUMN skyrgn INT DEFAULT NULL; %SPLIT%
ALTER TABLE IMAGE ADD FOREIGN KEY (skyrgn) REFERENCES skyregion (id); %SPLIT%
ALTER TABLE IMAGE DROP COLUMN centre_ra; %SPLIT%
ALTER TABLE IMAGE DROP COLUMN centre_decl; %SPLIT%
ALTER TABLE IMAGE DROP COLUMN x; %SPLIT%
ALTER TABLE IMAGE DROP COLUMN y; %SPLIT%
ALTER TABLE IMAGE DROP COLUMN z; %SPLIT%


CREATE FUNCTION cartesian(ira DOUBLE
                         ,idecl DOUBLE
                         ) RETURNS TABLE (x DOUBLE
                                         ,y DOUBLE
                                         ,z DOUBLE
                                          )
BEGIN
  RETURN TABLE (
     SELECT  COS(RADIANS(idecl))*COS(RADIANS(ira)) AS x
            ,COS(RADIANS(idecl))*SIN(RADIANS(ira)) AS y
            ,SIN(RADIANS(idecl)) AS z
           )
           ;
END;
%SPLIT%

CREATE FUNCTION updateSkyRgnMembers(isky_rgn_id INTEGER) RETURNS DOUBLE
BEGIN

  
  DECLARE inter, inter_sq DOUBLE;
  
  DELETE 
    FROM assocskyrgn
   WHERE assocskyrgn.skyrgn = isky_rgn_id
  ;
  
  SET inter = (SELECT  2.0*SIN(RADIANS(xtr_radius)/2.0)  
                    FROM skyregion 
                   WHERE id=isky_rgn_id);
  
  SET inter_sq = inter*inter;

  INSERT INTO assocskyrgn
  	(
  	runcat
  	,skyrgn
  	,distance_deg
  	) 
  SELECT rc.id as runcat
        ,sky.id as skyrgn
        ,DEGREES(2 * ASIN(SQRT( (rc.x - sky.x) * (rc.x - sky.x)
                       			+ (rc.y - sky.y) * (rc.y - sky.y)
                       			+ (rc.z - sky.z) * (rc.z - sky.z)
                      		  ) / 2 )
          		 )  
    FROM skyregion sky
    	,runningcatalog rc
   WHERE sky.id = isky_rgn_id
     AND rc.dataset = sky.dataset
   	 AND rc.wm_decl BETWEEN sky.centre_decl - sky.xtr_radius
                        AND sky.centre_decl + sky.xtr_radius
 	 AND (  (rc.x - sky.x) * (rc.x - sky.x)
            + (rc.y - sky.y) * (rc.y - sky.y)
            + (rc.z - sky.z) * (rc.z - sky.z)
         ) < inter_sq
  ;
  
  RETURN inter;

END;
%SPLIT%

CREATE FUNCTION getSkyRgn(idataset INTEGER
                         ,icentre_ra DOUBLE
                         ,icentre_decl DOUBLE
                         ,ixtr_radius DOUBLE
                       ) RETURNS INT

BEGIN

  DECLARE nskyrgn INT;
  DECLARE oskyrgnid INT;

  SELECT COUNT(*)
    INTO nskyrgn
    FROM skyregion
   WHERE dataset = idataset
     AND centre_ra = icentre_ra
     AND centre_decl = icentre_decl
     AND xtr_radius = ixtr_radius 
  ;

  IF nskyrgn = 1 THEN
    SELECT id
      INTO oskyrgnid
      FROM skyregion
     WHERE dataset = idataset
	   AND centre_ra = icentre_ra
	   AND centre_decl = icentre_decl
	   AND xtr_radius = ixtr_radius 
    ;
  ELSE
    SELECT NEXT VALUE FOR seq_skyregion INTO oskyrgnid;

    INSERT INTO skyregion
      (id
      ,dataset
      ,centre_ra
      ,centre_decl
      ,xtr_radius
      ,x
      ,y
      ,z
      ) 
    SELECT oskyrgnid
	      ,idataset
	      ,icentre_ra
	      ,icentre_decl
	      ,ixtr_radius
	      ,cart.x
	      ,cart.y
	      ,cart.z
    FROM (SELECT *
		  FROM cartesian(icentre_ra,icentre_decl)
		  ) cart
    ;
    
  DECLARE dummy DOUBLE;
  SELECT updateSkyRgnMembers(oskyrgnid)
  	INTO dummy;
    
  END IF;

  RETURN oskyrgnid;

END;
%SPLIT%



CREATE FUNCTION insertImage(idataset INT
                           ,itau_time DOUBLE
                           ,ifreq_eff DOUBLE
                           ,ifreq_bw DOUBLE
                           ,itaustart_ts TIMESTAMP
                           ,ibeam_maj DOUBLE
                           ,ibeam_min DOUBLE
                           ,ibeam_pa DOUBLE
                           ,iurl VARCHAR(1024)
                           ,icentre_ra DOUBLE
                           ,icentre_decl DOUBLE
                           ,ixtr_radius DOUBLE
                           ) RETURNS INT
BEGIN

  DECLARE iimageid INT;
  DECLARE oimageid INT;
  DECLARE iband SMALLINT;
  DECLARE itau INT;
  DECLARE iskyrgn INT;

  SET iband = getBand(ifreq_eff, ifreq_bw);
  SET iskyrgn = getSkyRgn(idataset, icentre_ra, icentre_decl, ixtr_radius);
  
  SELECT NEXT VALUE FOR seq_image INTO iimageid;

  INSERT INTO image
    (id
    ,dataset
    ,band
    ,tau_time
    ,freq_eff
    ,freq_bw
    ,taustart_ts
    ,skyrgn
    ,bmaj_syn
    ,bmin_syn
    ,bpa_syn
    ,url
    ) 
  VALUES
    (iimageid
    ,idataset
    ,iband
    ,itau_time
    ,ifreq_eff
    ,ifreq_bw
    ,itaustart_ts
    ,iskyrgn
    ,ibeam_maj 
    ,ibeam_min 
    ,ibeam_pa 
    ,iurl
    )
  ;

  SET oimageid = iimageid;
  RETURN oimageid;

END;
