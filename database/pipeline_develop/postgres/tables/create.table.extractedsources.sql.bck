/**
 * This table contains all the extracted sources during an observation.
 * Maybe source is not the right description, because measurements
 * may be made that were erronous and do not represent a source.
 *
 * This table is empty BEFORE an observation.
 * DURING an observation new sources are inserted into this table
 * AFTER an observation this table is dumped and transported to the 
 * catalog database
 *
 * xtrsrcid         Every inserted source/measurement gets a unique id.
 * image_id         The reference id to the image from which this sources
 *                  was extracted.
 * zone             The zone number in which the source declination resides.
 *                  The width of the zones is determined by the "zoneheight" 
 *                  parameter defined in the zoneheight table.
 * ra               Right ascension of the measurement [in degrees]
 * decl             Declination of the measurement [in degrees]
 * ra_err           The 1sigma error of the ra measurement [in arcsec]
 * decl_err         The 1sigma error of the declination measurement [in arcsec]
 * x, y, z:         Cartesian coordinate representation of (ra,decl)
 * margin           Used for association procedures to take into 
 *                  account sources that lie close to ra=0 & ra=360 meridian.
 *                  True: source is close to ra=0 meridian
 *                  False: source is far away enough from the ra=0 meridian
 *                  TODO: This is not implemented yet.
 * det_sigma:       The sigma level of the detection,
 *                  20*(I_peak/det_sigma) gives the rms of the detection.
 * semimajor        Semi-major axis that was used for gauss fitting
 *                  [in arcsec]
 * semiminor        Semi-minor axis that was used for gauss fitting
 *                  [in arcsec]
 * pa               Position Angle that was used for gauss fitting 
 *                  [from north through local east, in degrees]
 * I,Q,U,V          Stokes parameters
 *  peak            peak values
 *  int             integrated values
 *  err             1sigma errors
 *                  Fluxes and flux errors are in Jy
 * 
 */
CREATE TABLE extractedsources 
  (xtrsrcid SERIAL PRIMARY KEY
  ,image_id INT NOT NULL
  ,zone INT NOT NULL
  ,ra double precision NOT NULL
  ,decl double precision NOT NULL
  ,ra_err double precision NOT NULL
  ,decl_err double precision NOT NULL
  ,x double precision NOT NULL
  ,y double precision NOT NULL
  ,z double precision NOT NULL
  ,margin BOOLEAN NOT NULL DEFAULT false
  ,det_sigma double precision NOT NULL
  ,semimajor double precision NULL
  ,semiminor double precision NULL
  ,pa double precision NULL
  ,I_peak double precision NULL
  ,I_peak_err double precision NULL
  ,Q_peak double precision NULL
  ,Q_peak_err double precision NULL
  ,U_peak double precision NULL
  ,U_peak_err double precision NULL
  ,V_peak double precision NULL
  ,V_peak_err double precision NULL
  ,I_int double precision NULL
  ,I_int_err double precision NULL
  ,Q_int double precision NULL
  ,Q_int_err double precision NULL
  ,U_int double precision NULL
  ,U_int_err double precision NULL
  ,V_int double precision NULL
  ,V_int_err double precision NULL
  ,id INT NULL
  ,FOREIGN KEY (image_id) REFERENCES images (imageid)
  )
;

