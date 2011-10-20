--DROP TABLE loadxtrsources;
/**
 * This table contains all the extracted sources during an observation.
 * To check whether a source is new, transient or variable comparisons 
 * with the catalogsources table must be made.
 *
 * This table is empty BEFORE an observation
 * DURING an observation new sources are inserted into this table
 * AFTER an observation this table is dumped and transported to the 
 * catalog database
 *
 * tau:             The integration time (one out of the logarithmic series)
 * band:            The frequency band (freq_eff)
 * seq_nr:          Stream of images with same tau are ordered by 
 *                  sequence number
 * ds_id:           Determines the dataset from which this source comes
 * zone:            The declination zone (decl)
 * assoc_xtrsrcid:  To which src (in this table) this xtrsrcid is associated
 * assoc_catsrcid:  To which src (in the catalogsource table) this xtrsrcid 
 *                  is associated
 * x, y, z:         Cartesian coordinates
 * det_sigma:       The sigma level of the detection,
 *                  20*(I_peak/det_sigma) gives the rms of the detection.
 * Fluxes and errors are in Jy
 * ra, decl are in degrees 
 * ra_err and decl_err are in arcsec.
 * 
 */
CREATE TABLE loadxtrsources 
  (limage_id INT NOT NULL
  ,lra double precision NOT NULL
  ,ldecl double precision NOT NULL
  ,lra_err double precision NOT NULL
  ,ldecl_err double precision NOT NULL
  ,lI_peak double precision NULL
  ,lI_peak_err double precision NULL
  ,lI_int double precision NULL
  ,lI_int_err double precision NULL
  ,ldet_sigma double precision NOT NULL
/*  ,lzoneheight double precision NOT NULL DEFAULT 1*/
  )
;

