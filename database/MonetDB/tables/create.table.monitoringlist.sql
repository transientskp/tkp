--DROP TABLE monitoringlist;
/* This table contains the list of sources that are monitored.
 * This implies that the source finder software will measure the flux
 * in an image at exactly the given position.
 * These positions are 0 by default, since they can be retrieved by
 * joining with the runningcatalog.
 * For user defined sources, however, positions may be available that 
 * are more precise than those in the runningcatalog. Hence the
 * ra and decl columns are still necessary for these sources.
 * The xtrsrc_id refers to the xtrsrc_id in the runningcatalog,
 * when available. Eg, manually inserted sources with positions
 * obtained differently will not have an xtrsrc_id to start with 
 * (hence the default of -1), until the first time the flux has been
 * measured; then these sources (even when actual upper limits) will be 
 * inserted into extractedsources and runningcatalog, and have an xtrsrc_id.
 * They will still have userentry set to true, so that the position
 * used is that in this table (the more precise position), not that 
 * of the runningcatalog.
 */

CREATE SEQUENCE "seq_monitoringlist" AS INTEGER;

CREATE TABLE monitoringlist
  (monitorid INTEGER NOT NULL DEFAULT NEXT VALUE FOR "seq_monitoringlist"
  ,xtrsrc_id INTEGER 
  ,ra DOUBLE PRECISION DEFAULT 0
  ,decl DOUBLE PRECISION DEFAULT 0
  ,ds_id INTEGER NOT NULL
  ,userentry BOOLEAN DEFAULT FALSE
  ,PRIMARY KEY (monitorid)
  )
;
