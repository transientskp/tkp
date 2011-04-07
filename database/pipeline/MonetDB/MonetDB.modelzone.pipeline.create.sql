/*
 * The Transient Key Project pipeline uses two databases, 
 * one for storing data temporarily in a working area called the "pipeline" database,
 * and the other as a permanent database for catalogue and data mining purposes called the "catalog" database.
 *
 * This scripts creates the TKP "pipeline" database.
 * (Run it on the command line as follows:
 * %>mysql -ulofar -pcs1 < MySQLInnoDB.modelpipeline.create.sql
 *
 * A typical observation run deals with the "pipeline" database as follows:
 * () Before observation - Init the database
 * 	- drop the database (or recreate it)
 * 	- create all the tables
 * 	- insert all the sources from the catalog database (these include our own LOFAR catalogue as well as others) 
 * 		that will be expected in this specific observation
 * 	- determine @zoneheight and @theta for this observation (it might be changed any time, but that will cost 
 * 		extra computing time)
 * 	- call the procedure BuildZoneIndex(zoneheight, theta) to fill the spatial search tables
 *		This will order the catalogue sources by zone (dec) and ra.
 * () During observation - Use the database
 * 	- All extracted sources will be inserted into the EXTRACTEDSOURCES table
 * 	- Transient detection 
 * 		Extracted sources (Objects) will be compared with the catalogue sources (Sources)
 * 		(ra, dec) + their errors + distance of Object to neighbor sources are queried
 * 		TODO: This is not worked out fully yet.
 * () After observation - Dump data into files
 * 	- Load data into "catalog" database
 *
 * Bart Scheers, 2008-02-18
 *
 */

/**
 * A work-around, because of a MonetDB bug 
 * (CREATE/ALTER SCHEMA does not work properly, resulting in created 
 * tables (from whatever SCHEMA) to fall under the sys SCHEMA)
 * TODO: When will CWI fix this bug?
 */
DROP USER "lofar";

--DROP SCHEMA modelzonepipeline;

DROP TABLE extractedsources;
DROP TABLE cataloguesources;
DROP TABLE catalogues;
DROP TABLE associatedsources;
DROP TABLE frequencybands;
DROP TABLE datasets;
DROP TABLE resolutions;
DROP TABLE observations;
DROP TABLE versions;

DROP TABLE zoneheight;
DROP TABLE zones;
DROP TABLE zoneindex;
DROP TABLE zonezone;

DROP FUNCTION alpha;

CREATE USER "lofar" WITH PASSWORD 'cs1' NAME 'lofar database' SCHEMA "sys";

--CREATE SCHEMA "modelzonepipeline" AUTHORIZATION "lofar";

--ALTER USER "lofar" SET SCHEMA "modelzonepipeline";

/**
 * End of work-around
 */

/**
 * This table keeps track of the versions and changes
 */
CREATE TABLE versions (
  versionid INT NOT NULL AUTO_INCREMENT,
  version VARCHAR(32) NULL,
  scriptname VARCHAR(256) NULL,
  PRIMARY KEY (versionid)
);

INSERT INTO versions (version, scriptname) VALUES ('0.0.1', '/scratch/bscheers/databases/design/sql/MonetDB.modelzone.pipeline.create.sql');

/*
 * This table contains the information about the current observation
 * time_s:	BIGINT is used to simulate a ms accurate time
stamp
 */
CREATE TABLE observations (
  obsid INT NOT NULL AUTO_INCREMENT,
  time_s BIGINT NULL,
  time_e BIGINT  NULL,
  description VARCHAR(500) NULL,
  PRIMARY KEY (obsid)
);

/*
 * This table contains the information about the resolutions obtained in this observation
 */
CREATE TABLE resolutions (
  resid INT  NOT NULL,
  major DOUBLE NOT NULL,
  minor DOUBLE NOT NULL,
  pa DOUBLE NOT NULL,
  PRIMARY KEY (resid)
);

/*
 * This table contains the frequencies at which the extracted sources were detected.
 * It might also be preloaded with the frequencies at which the stokes of the 
 * catalogue sources were measured.
 */
CREATE TABLE frequencybands (
  freqbandid INT NOT NULL AUTO_INCREMENT,
  freq_low DOUBLE DEFAULT NULL,
  freq_high DOUBLE DEFAULT NULL,
  PRIMARY KEY (freqbandid)
);

/*
 * This table contains the information about the dataset that is produced by LOFAR. 
 * A dataset has an integration time and consists of multiple frequency layers.
 * taustart_timestamp: 	the start time of the integration
 */
CREATE TABLE datasets (
  dsid INT NOT NULL,
  obs_id INT NOT NULL,
  res_id INT NOT NULL,
  dstype TINYINT NOT NULL,
  taustart_timestamp BIGINT NOT NULL,
  dsinname CHAR(15) NOT NULL,
  dsoutname CHAR(15) DEFAULT NULL,
  desription VARCHAR(100) DEFAULT NULL,
  PRIMARY KEY (dsid),
  FOREIGN KEY (obs_id) REFERENCES observations(obsid),
  FOREIGN KEY (res_id) REFERENCES resolutions(resid)
);

/*
 * This table contains the layers that belong to a dataset.
 * Each layer has its effective frequency, and contains the sources
 * that will be detected by the source extraction.
 */
/*CREATE TABLE dslayers (
  layerid INT  NOT NULL,
  ds_id INT  NOT NULL,
  freq_id INT  NOT NULL,
  PRIMARY KEY (layerid),
  INDEX (ds_id),
  FOREIGN KEY (ds_id) REFERENCES datasets(dsid),
  INDEX (freq_id),
  FOREIGN KEY (freq_id) REFERENCES frequencybands(freqid)
) ENGINE=InnoDB;
*/

/*
 *
 */
CREATE TABLE catalogues (
  catid TINYINT  NOT NULL AUTO_INCREMENT,
  catname VARCHAR(50) NOT NULL,
  PRIMARY KEY (catid)
);

/*
 * This table contains the known sources that were detected previously, either 
 * by LOFAR itself or other instruments. 
 * It is a selection from the table containing all the catalogue sources 
 * (in the catlogue area). 
 * Every observation has its field of view and for this all the known sources are collected.
 * This table will be loaded from the catalogue table in the catalogue database
 * before every observation.
 * This table will be used to load the sources table and will not be touched 
 * any more during an observation.
 */
CREATE TABLE cataloguesources (
  catsrcid INT  NOT NULL AUTO_INCREMENT,
  class_id TINYINT  NOT NULL,
  cat_id TINYINT  NOT NULL,
  band INT  NOT NULL,
  ra DOUBLE NOT NULL,
  decl DOUBLE NOT NULL,
  ra_err DOUBLE NOT NULL,
  decl_err DOUBLE NOT NULL,
  I_avg DOUBLE NOT NULL,
  I_avg_err DOUBLE NULL,
  I_min DOUBLE NOT NULL,
  I_min_err DOUBLE NULL,
  I_max DOUBLE NOT NULL,
  I_max_err DOUBLE NULL,
  PRIMARY KEY (catsrcid),
  FOREIGN KEY (cat_id) REFERENCES catalogues(catid),
  FOREIGN KEY (band) REFERENCES frequencybands(freqbandid)
);

/*
 * This table contains all the extracted sources during an observation.
 * To check whether a source is new, transient or variable comparisons with the 
 * cataloguesources table must be made.
 *
 * This table is empty BEFORE an observation
 * DURING an observation new sources are inserted into this table
 * AFTER an observation this table is dumped and transported to the catalogue database
 * tau:		The integration time (one out of the logarithmic series)
 * band:	The frequency band (freq_eff)
 * seq_nr:	Stream of images with same tau are ordered by sequence number
 * ds_id:	determines the dataset from which this source comes
 * zone:	The declination zone in which decl falls
 * x, y, z:	Cartesian coordinates
 */
CREATE TABLE extractedsources (
  tau INT NOT NULL,
  band INT NOT NULL,
  seq_nr INT NOT NULL,
  xtrsrcid INT NOT NULL AUTO_INCREMENT,
  ds_id INT NOT NULL,
  zone INT NOT NULL,
  freq_eff DOUBLE NOT NULL,
  class_id TINYINT NULL,
  margin BOOLEAN NOT NULL DEFAULT 0,
  ra DOUBLE NOT NULL,
  decl DOUBLE NOT NULL,
  ra_err DOUBLE NOT NULL,
  decl_err DOUBLE NOT NULL,
  x DOUBLE NOT NULL,
  y DOUBLE NOT NULL,
  z DOUBLE NOT NULL,
  I DOUBLE NOT NULL,
  Q DOUBLE NULL,
  U DOUBLE NULL,
  V DOUBLE NULL,
  I_err DOUBLE NOT NULL,
  Q_err DOUBLE NULL,
  U_err DOUBLE NULL,
  V_err DOUBLE NULL,
  PRIMARY KEY (tau
             ,band
             ,seq_nr
             ,xtrsrcid
             ),
  FOREIGN KEY (band) REFERENCES frequencybands(freqbandid),
  FOREIGN KEY (ds_id) REFERENCES datasets(dsid)
);

/*
 * This table contains all the extracted sources that could be associated with
 * other sources.
 *
 */
CREATE TABLE associatedsources (
  tau INT NOT NULL,
  band INT NOT NULL,
  seq_nr INT NOT NULL,
  xtrsrcid INT NOT NULL,
  assocsrcid INT NOT NULL,
  PRIMARY KEY (tau
              ,band
              ,seq_nr
              ,xtrsrcid
              )
);

/* 
 *                      +------------------------------------------------------+
 *                      | This part creates the tables for the Zones Algorithm |
 *                      +------------------------------------------------------+
 * From J.Gray et al. "The Zones Algorithm for Finding Points-Near-a-Point or Cross-Matching Spatial Datasets", 
 * MSR TR 2006 52, April 2006.
 *
 * Create and populate the Zone index tables:
 * The procedure BuildZoneIndex() populates these tables.
 * zoneheight:	contains zoneheight constant used by the algorithm.
 * 		You can update zoneheight and then call BuildZoneIndex(newZoneHeight)
 * 		to rebuild the indices
 * zoneindex: 	a table that maps type-zone-longitude to objects
 * 		it indexes the Place and Station table in this example
 * Zone: 	a table of with a row for each zone giving latMin, latMax, Alpha
 * ZoneZone: 	Maps each zone to all zones it may have a cross-match with.
 */

/*
 * Use a zone height drives the parameters of all the other tables.
 * Invoke BuidZoneIndex(NewZoneHeight) to change height and rebuild the indices
 * zoneheight: 	units in degrees
 */
CREATE TABLE zoneheight ( 
  zoneheight DOUBLE NOT NULL
);

/*
 * Zone table has a row for each zone.
 * It is used to force the query optimizer to pick the right plan
 * zone:	FLOOR(decl_min/zoneHeight)
 * decl_min:	min declination of this zone (degrees)
 * decl_max:	max declination of this zone (degrees)
 */
CREATE TABLE zones (
  zone INT NOT NULL,
  decl_min DOUBLE,
  decl_max DOUBLE,
  PRIMARY KEY(zone)
);

/*
 * Zone-based spatial index for Places and Stations.
 * Note the key is on objectType ('S' or 'P' for station or place in out case)
 * then zone to give the band to search in
 * then longitude to give an offset in the band.
 * then objID to give a unique key
 * It copies the spherical and cartesian coordianates from the base objects
 * it also has a flag indicating if this is a "margin" element, to solve
 * the warp-araound problem.
 * TODO: the types need still be specified
 * 	- 'C' = catalogue source
 * 	- 'X' = extracted source
 * objType:	TODO: the types need still be specified
 * objid:	object Identifier in table
 * zone:	zone number (using 10 arcminutes)
 * ra:		sperical coordinates
 * x,y,z:	cartesian coordinates
 * margin:	"margin" or "native" elements
 */

CREATE TABLE zoneindex (
  objType CHAR(1) NOT NULL,
  objid INT NOT NULL,
  zone INT NOT NULL,
  ra DOUBLE NOT NULL,
  decl DOUBLE NOT NULL,
  x DOUBLE NOT NULL,
  y DOUBLE NOT NULL,
  z DOUBLE NOT NULL,
  margin BOOLEAN NOT NULL,
  PRIMARY KEY (objType
	      ,zone
	      ,ra
	      ,objid)
);


/*
 * ZoneZone table maps each zone to zones which may have a cross match
 */
CREATE TABLE zonezone (
  zone1 INT, 
  zone2 INT, 
  alpha DOUBLE,
  PRIMARY KEY (zone1
	      ,zone2)
);

/*
 * Here we define the function alpha(theta, decl),
 * and the procedure BuildZoneIndex(zoneheight, theta)
 */


--DELIMITER //

/*
 * This function computes the ra expansion for for a given theta at a given declination.
 * theta and decl, both in degrees.
 */
CREATE FUNCTION alpha(theta DOUBLE, decl DOUBLE) RETURNS DOUBLE 
BEGIN
	IF ABS(decl) + theta > 89.9 
		THEN RETURN 180 ;
		ELSE RETURN ABS(ATAN(SIN((theta * (pi() / 180) )) / SQRT(ABS(COS(((decl - theta) * (pi() / 180))) * COS(((decl + theta) * (pi() / 180))))))) * (180 / pi()) ; 
	END IF ;
END;

/*
CREATE PROCEDURE InitObservation()
BEGIN
  CALL LoadCatSources();
END;
//

CREATE PROCEDURE LoadCatSources()
BEGIN
--Start here
END;
//
*/
/*
 * Procedure to populate the zone index.
 * If you want to change the zoneHeight, call this function to rebuild all
 * the index tables. @zoneHeight is in degrees.
 * @theta is the radius of cross-match, often @theta == @zoneHeight
 * Note the subtle difference between the value zoneHeight and the table zoneheight
 */
/*
CREATE PROCEDURE BuildZoneIndex(IN zh DOUBLE, IN theta DOUBLE)
BEGIN

  DECLARE maxZone INT;
  DECLARE minZone INT;
  DECLARE zones INT; -- number of neighboring zones for cross match

-- Empty all the existing index tables 
  DELETE FROM zoneheight;
  DELETE FROM zone;
  --DELETE FROM zoneindex;
  DELETE FROM zonezone;

-- record the ZoneHeight in the ZoneHeight table 
  INSERT INTO zoneheight (zoneheight) VALUES (zh);

-- fill the zone table (used to help SQL optimizer pick the right plan) 
  SET maxZone = FLOOR((90.0 + zh) / zh);
  SET minZone = - maxZone;
  WHILE minZone < maxZone DO
    INSERT INTO zone VALUES (minZone, minZone * zh, (minZone + 1) * zh);
    SET minZone = minZone + 1;
  END WHILE;

/* 
 * Create the index for the Catalogue table 
 * /
  INSERT INTO zoneindex
    SELECT 'C'
	  ,catsrcid
	  ,FLOOR(decl/zh) AS zone
	  ,ra
	  ,decl
	  ,COS(RADIANS(decl))*COS(RADIANS(ra)) AS x
	  ,COS(RADIANS(decl))*SIN(RADIANS(ra)) AS y
	  ,SIN(RADIANS(decl)) AS z
	  ,0 AS margin
     FROM cataloguesources;

/* 
 * Create the index for the X table (these are the extracted sources).
 * /
  INSERT INTO zoneindex
    SELECT 'X'
          ,xtrsrcid
          ,FLOOR(decl/zh) AS zone
          ,ra
          ,decl
          ,COS(RADIANS(decl))*COS(RADIANS(ra)) AS x
          ,COS(RADIANS(decl))*SIN(RADIANS(ra)) AS y
          ,SIN(RADIANS(decl)) AS z
          ,0 AS margin
     FROM extractedsources;

/*
 * now add left and right marginal sources
 * You could limit the margin width use alpha(MaxTheta,zone.maxdecl)
 * if you knew MaxTheta; 
 * but, we do not know MaxTheta so we use 180
 * /
  INSERT INTO zoneindex
    SELECT objType
	  ,objid
	  ,zone
	  ,ra - 360.0
	  ,decl
	  ,x
	  ,y
	  ,z
	  ,1 AS margin 
     FROM zoneindex 
    WHERE ra >= 180 
    UNION
    SELECT objType
	  ,objid
	  ,zone
	  ,ra + 360.0
	  ,decl
	  ,x
	  ,y
	  ,z
	  ,1 AS margin 
     FROM zoneindex 
    WHERE ra < 180;

-- ZoneZone table maps each zone to zones which may have a cross match 
  SET zones = CEILING(theta/zh);	-- (generally = 1)
-- For each pair, compute min/max decl and alpha
  INSERT INTO zonezone 
    SELECT z1.zone
	  ,z2.zone
	  ,CASE WHEN z1.declMin < 0 THEN alpha(theta, z1.declMin)
		ELSE alpha(theta, z1.declMax) 
		END
      FROM zone z1 JOIN zone z2
        ON z2.zone BETWEEN z1.zone - zones AND z1.zone + zones;

END;
//

DELIMITER ;

/*
 * Initial call to build the zone index with a height of 10 arcMinutes.
 * and a self-match or cross-match radius of 1 degree (60 nautical miles).
 */
--DECLARE zoneHeight DOUBLE;
--DECLARE theta DOUBLE;
--SET theta = 60.0 / 60.0;
--SET zoneHeight = 10.0 / 60.0;

--CALL BuildZoneIndex(1/6, 1);

/*
 * Define and use Points-Near-Point Function
 * /
DELIMITER //
/*
 * GetNearbyObjects() returns objects of type @type in { 'P', 'S'}
 * that are within @theta degrees of (ra, decl).
 * The returned table includes the distance to the object.
 */
/*CREATE PROCEDURE GetNearbyObjects(IN type CHAR(1), IN ra DOUBLE, IN decl DOUBLE, IN theta DOUBLE)
NOT DETERMINISTIC
MODIFIES SQL DATA
BEGIN

  DECLARE zh, alfa, x, y, z DOUBLE;

  CREATE TEMPORARY TABLE getnearobjs (
    objID INT,
    distance DOUBLE,
    PRIMARY KEY (objID)
  ) ENGINE=InnoDB

  SELECT min(zoneheight) INTO zh FROM zoneheight;

  SELECT alpha(theta, decl)
	,COS(RADIANS(decl))*COS(RADIANS(ra))
	,COS(RADIANS(decl))*SIN(RDAIANS(ra))
	,SIN(RADIANS(decl))
    INTO alfa
	,x
	,y
	,z;


-- get zone height from constant table. 

-- compute "alpha" expansion and cartesian coordinates.

/*-- insert the objects in the answer table.
insert @objects
select objID,
case when(@x*x +@y*y + @z*z) < 1 -- avoid domain error on acos
then degrees(acos(@x*x +@y*y + @z*z))
else 0 end -- when angle is tiny.
from Zone Z -- zone nested loop with
inner loop join ZoneIndex ZI on Z.zone = ZI.zone -- zoneIndex
where objType = @type -- restrict to type ?P? or ?S?
and Z.latMin between @lat-@theta-@zoneHeight -- zone intersects
and @lat+@theta -- the theta circle
and ZI.lon between @lon-@alpha -- restrict to a 2 Alpha wide
and @lon + @alpha -- longitude band in the zone
and ZI.lat between @lat-@theta -- and roughly correct latitude
and @lat + @theta
and (@x*x +@y*y + @z*z) -- and then a careful distance
> cos(radians(@theta)) -- distance test
return

RETURN 90.0;

END;
//

*/
--DELIMITER ;

/*
 * The End.
 */

