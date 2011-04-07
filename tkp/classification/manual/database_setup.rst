.. _database_setup:

Database setup
==============

Below are the SQL commands I use to create all the tables I need to
run the pipeline. This almost completely resets everything, since it
drops tables and primary key sequences.

The important tables to pay attention to are ``tempbasesources``,
which has an extra column ``distance``, ``transients``, which stores
information about transients, and ``classification``, which keeps the
classification information around (currently in a very simple way).

::

    DROP TABLE versions cascade;
    DROP SEQUENCE "seq_versions";
    CREATE SEQUENCE "seq_versions" AS INTEGER;
    CREATE TABLE versions (
      versionid INT DEFAULT NEXT VALUE FOR "seq_versions",
      version VARCHAR(32) NULL,
      creation_date DATE NOT NULL,
      scriptname VARCHAR(256) NULL,
      PRIMARY KEY (versionid)
    );
    
    
    DROP TABLE frequencybands cascade;
    DROP SEQUENCE "seq_frequencybands";
    CREATE SEQUENCE "seq_frequencybands" AS INTEGER;
    CREATE TABLE frequencybands (
      freqbandid INT NOT NULL DEFAULT NEXT VALUE FOR "seq_frequencybands",
      freq_low DOUBLE DEFAULT NULL,
      freq_high DOUBLE DEFAULT NULL,
      PRIMARY KEY (freqbandid)
    );
    
    
    DROP TABLE datasets cascade;
    DROP SEQUENCE "seq_datasets";
    CREATE SEQUENCE "seq_datasets" AS INTEGER;
    CREATE TABLE datasets (
      dsid INT DEFAULT NEXT VALUE FOR "seq_datasets",
      rerun INT NOT NULL DEFAULT '0',
      dstype TINYINT NOT NULL,
      process_ts TIMESTAMP NOT NULL, 
      dsinname VARCHAR(64) NOT NULL,
      dsoutname VARCHAR(64) DEFAULT NULL,
      description VARCHAR(100) DEFAULT NULL,
      PRIMARY KEY (dsid)
    );
    
    
    DROP TABLE images cascade;
    DROP SEQUENCE "seq_images";
    CREATE SEQUENCE "seq_images" AS INTEGER;
    CREATE TABLE images 
      (imageid INT DEFAULT NEXT VALUE FOR "seq_images"
      ,ds_id INT NOT NULL
      ,tau INT NOT NULL
      ,band INT NOT NULL
      ,tau_time DOUBLE NOT NULL
      ,freq_eff DOUBLE NOT NULL
      ,freq_bw DOUBLE NULL
      ,taustart_ts TIMESTAMP NOT NULL
      ,url VARCHAR(120) NULL
      ,PRIMARY KEY (imageid)
      ,FOREIGN KEY (ds_id) REFERENCES datasets (dsid)
      ,FOREIGN KEY (band) REFERENCES frequencybands (freqbandid)
      )
    ;
    
    
    DROP TABLE associationclass cascade;
    CREATE TABLE associationclass (
      assoc_classid INT NOT NULL,
      type INT NOT NULL,
      assoc_class VARCHAR(10) DEFAULT NULL,
      description VARCHAR(100) DEFAULT NULL,
      PRIMARY KEY (assoc_classid)
    );
    
    DROP TABLE catalogs cascade;
    DROP SEQUENCE "seq_catalogs";
    CREATE SEQUENCE "seq_catalogs" AS INTEGER;
    CREATE TABLE catalogs (
      catid INT DEFAULT NEXT VALUE FOR "seq_catalogs",
      catname VARCHAR(50) NOT NULL,
      fullname VARCHAR(250) NOT NULL,
      PRIMARY KEY (catid)
    );
    
    
    DROP TABLE catalogedsources cascade;
    DROP SEQUENCE "seq_catalogedsources";
    CREATE SEQUENCE "seq_catalogedsources" AS INTEGER;
    CREATE TABLE catalogedsources (
      catsrcid INT DEFAULT NEXT VALUE FOR "seq_catalogedsources",
      cat_id INT NOT NULL,
      orig_catsrcid INT NOT NULL,
      catsrcname VARCHAR(120) NULL,
      tau INT NULL,
      band INT NOT NULL,
      freq_eff DOUBLE NOT NULL,
      zone INT NOT NULL,
      ra DOUBLE NOT NULL,
      decl DOUBLE NOT NULL,
      ra_err DOUBLE NOT NULL,
      decl_err DOUBLE NOT NULL,
      x DOUBLE NOT NULL,
      y DOUBLE NOT NULL,
      z DOUBLE NOT NULL,
      margin BOOLEAN NOT NULL DEFAULT 0,
      det_sigma DOUBLE NOT NULL DEFAULT 0,
      src_type VARCHAR(1) NULL,
      fit_probl VARCHAR(2) NULL,
      ell_a DOUBLE NULL,
      ell_b DOUBLE NULL,
      PA DOUBLE NULL,
      PA_err DOUBLE NULL,
      major DOUBLE NULL,
      major_err DOUBLE NULL,
      minor DOUBLE NULL,
      minor_err DOUBLE NULL,
      I_peak_avg DOUBLE NULL,
      I_peak_avg_err DOUBLE NULL,
      I_peak_min DOUBLE NULL,
      I_peak_min_err DOUBLE NULL,
      I_peak_max DOUBLE NULL,
      I_peak_max_err DOUBLE NULL,
      I_int_avg DOUBLE NULL,
      I_int_avg_err DOUBLE NULL,
      I_int_min DOUBLE NULL,
      I_int_min_err DOUBLE NULL,
      I_int_max DOUBLE NULL,
      I_int_max_err DOUBLE NULL,
      frame VARCHAR(20) NULL,
      PRIMARY KEY (catsrcid),
      UNIQUE (cat_id ,orig_catsrcid),
      FOREIGN KEY (cat_id) REFERENCES catalogs (catid),
      FOREIGN KEY (band) REFERENCES frequencybands (freqbandid)
    );
    
    
    DROP TABLE extractedsources cascade;
    DROP SEQUENCE "seq_extractedsources";
    CREATE SEQUENCE "seq_extractedsources" AS INTEGER;
    CREATE TABLE extractedsources 
      (xtrsrcid INT DEFAULT NEXT VALUE FOR "seq_extractedsources"
      ,image_id INT NOT NULL
      ,zone INT NOT NULL
      ,ra DOUBLE NOT NULL
      ,decl DOUBLE NOT NULL
      ,ra_err DOUBLE NOT NULL
      ,decl_err DOUBLE NOT NULL
      ,x DOUBLE NOT NULL
      ,y DOUBLE NOT NULL
      ,z DOUBLE NOT NULL
      ,margin BOOLEAN NOT NULL DEFAULT 0
      ,det_sigma DOUBLE NOT NULL
      ,I_peak DOUBLE NULL
      ,I_peak_err DOUBLE NULL
      ,Q_peak DOUBLE NULL
      ,Q_peak_err DOUBLE NULL
      ,U_peak DOUBLE NULL
      ,U_peak_err DOUBLE NULL
      ,V_peak DOUBLE NULL
      ,V_peak_err DOUBLE NULL
      ,I_int DOUBLE NULL
      ,I_int_err DOUBLE NULL
      ,Q_int DOUBLE NULL
      ,Q_int_err DOUBLE NULL
      ,U_int DOUBLE NULL
      ,U_int_err DOUBLE NULL
      ,V_int DOUBLE NULL
      ,V_int_err DOUBLE NULL
      ,PRIMARY KEY (xtrsrcid)
      ,FOREIGN KEY (image_id) REFERENCES images (imageid)
      )
    ;
    
    DROP TABLE loadxtrsources cascade;
    CREATE TABLE loadxtrsources 
      (limage_id INT NOT NULL
      ,lra DOUBLE NOT NULL
      ,ldecl DOUBLE NOT NULL
      ,lra_err DOUBLE NOT NULL
      ,ldecl_err DOUBLE NOT NULL
      ,lI_peak DOUBLE NULL
      ,lI_peak_err DOUBLE NULL
      ,lI_int DOUBLE NULL
      ,lI_int_err DOUBLE NULL
      ,ldet_sigma DOUBLE NOT NULL
      )
    ;
    
    
    DROP TABLE basesources cascade;
    CREATE TABLE basesources 
      (xtrsrc_id INT NOT NULL
      ,ds_id INT NOT NULL
      ,image_id INT NOT NULL
      ,zone INT NOT NULL
      ,ra DOUBLE NOT NULL
      ,decl DOUBLE NOT NULL
      ,ra_err DOUBLE NOT NULL
      ,decl_err DOUBLE NOT NULL
      ,x DOUBLE NOT NULL
      ,y DOUBLE NOT NULL
      ,z DOUBLE NOT NULL
      ,margin BOOLEAN NOT NULL DEFAULT 0
      ,beam_semimaj DOUBLE NULL
      ,beam_semimin DOUBLE NULL
      ,beam_pa DOUBLE NULL
      ,datapoints INT NULL
      ,I_peak_sum DOUBLE NULL
      ,I_peak_sq_sum DOUBLE NULL
      ,weight_peak_sum DOUBLE NULL
      ,weight_I_peak_sum DOUBLE NULL
      ,weight_I_peak_sq_sum DOUBLE NULL
      )
    ;
    
    
    DROP SEQUENCE "seq_tempbasesources";
    CREATE SEQUENCE "seq_tempbasesources" AS INTEGER;
    DROP TABLE tempbasesources cascade;
    CREATE TABLE tempbasesources 
    (
       tempsrcid INT DEFAULT NEXT VALUE FOR "seq_tempbasesources",
       xtrsrc_id INT NOT NULL
      ,assoc_xtrsrc_id INT NOT NULL
      ,distance DOUBLE NOT NULL
      ,datapoints INT NULL
      ,I_peak_sum DOUBLE NULL
      ,I_peak_sq_sum DOUBLE NULL
      ,weight_peak_sum DOUBLE NULL
      ,weight_I_peak_sum DOUBLE NULL
      ,weight_I_peak_sq_sum DOUBLE NULL
    )
    ;
    
    
    
    DROP TABLE lsm cascade;
    CREATE TABLE lsm (
      lsmid INT NOT NULL,
      cat_id INT NOT NULL,
      orig_catsrcid INT NOT NULL,
      catsrcname VARCHAR(120) NULL,
      tau INT NULL,
      band INT NOT NULL,
      freq_eff DOUBLE NOT NULL,
      zone INT NOT NULL,
      ra DOUBLE NOT NULL,
      decl DOUBLE NOT NULL,
      ra_err DOUBLE NOT NULL,
      decl_err DOUBLE NOT NULL,
      x DOUBLE NOT NULL,
      y DOUBLE NOT NULL,
      z DOUBLE NOT NULL,
      margin BOOLEAN NOT NULL DEFAULT 0,
      det_sigma DOUBLE NOT NULL DEFAULT 0,
      src_type VARCHAR(1) NULL,
      fit_probl VARCHAR(2) NULL,
      ell_a DOUBLE NULL,
      ell_b DOUBLE NULL,
      PA DOUBLE NULL,
      PA_err DOUBLE NULL,
      major DOUBLE NULL,
      major_err DOUBLE NULL,
      minor DOUBLE NULL,
      minor_err DOUBLE NULL,
      I_peak_avg DOUBLE NULL,
      I_peak_avg_err DOUBLE NULL,
      I_peak_min DOUBLE NULL,
      I_peak_min_err DOUBLE NULL,
      I_peak_max DOUBLE NULL,
      I_peak_max_err DOUBLE NULL,
      I_int_avg DOUBLE NULL,
      I_int_avg_err DOUBLE NULL,
      I_int_min DOUBLE NULL,
      I_int_min_err DOUBLE NULL,
      I_int_max DOUBLE NULL,
      I_int_max_err DOUBLE NULL,
      frame VARCHAR(20) NULL,
      PRIMARY KEY (lsmid),
      UNIQUE (cat_id ,orig_catsrcid)
    )
    ;
    
    
    DROP TABLE spectralindices cascade;
    DROP SEQUENCE "seq_spectralindices";
    CREATE SEQUENCE "seq_spectralindices" AS INTEGER;
    CREATE TABLE spectralindices 
      (spindxid INT DEFAULT NEXT VALUE FOR "seq_spectralindices"
      ,catsrc_id INT NOT NULL
      ,spindx_degree INT NOT NULL DEFAULT 0
      ,c0 DOUBLE NOT NULL DEFAULT 0
      ,c1 DOUBLE NULL DEFAULT 0
      ,c2 DOUBLE NULL DEFAULT 0
      ,c3 DOUBLE NULL DEFAULT 0
      ,c4 DOUBLE NULL DEFAULT 0
      ,c5 DOUBLE NULL DEFAULT 0
      ,PRIMARY KEY (spindxid)
      ,FOREIGN KEY (catsrc_id) REFERENCES catalogedsources (catsrcid)
      )
    ;
    
    
    
    DROP TABLE assoccatsources;
    CREATE TABLE assoccatsources
      (xtrsrc_id INT NOT NULL
      ,assoc_catsrc_id INT NULL
      ,assoc_weight DOUBLE NULL
      ,assoc_distance_arcsec DOUBLE NULL
      ,assoc_lr_method INT NULL DEFAULT 0
      ,assoc_r DOUBLE NULL
      ,assoc_lr DOUBLE NULL
      )
    ;
    
    DROP TABLE associationclass;
    CREATE TABLE associationclass (
      assoc_classid INT NOT NULL,
      type INT NOT NULL,
      assoc_class VARCHAR(10) DEFAULT NULL,
      description VARCHAR(100) DEFAULT NULL,
      PRIMARY KEY (assoc_classid)
    );
    
    DROP table assocxtrsources;
    CREATE TABLE assocxtrsources
      (xtrsrc_id INT NOT NULL
      ,assoc_xtrsrc_id INT NULL
      ,assoc_weight DOUBLE NULL
      ,assoc_distance_arcsec DOUBLE NULL
      ,assoc_lr_method INT NULL DEFAULT 0
      ,assoc_r DOUBLE NULL
      ,assoc_lr DOUBLE NULL
      )
    ;
    
    DROP table transients;
    DROP SEQUENCE "seq_transients";
    CREATE SEQUENCE "seq_transients" AS INTEGER;
    CREATE TABLE transients
      (
      transientid INT DEFAULT NEXT VALUE FOR "seq_transients"
      ,xtrsrc_id INT NOT NULL
      ,siglevel DOUBLE NULL DEFAULT 0
      ,status INT NULL DEFAULT 0
      ,t_start TIMESTAMP NULL
      )
    ;
    
    DROP TABLE classification;
    CREATE TABLE classification
    (
      transient_id INT NOT NULL
      ,classification VARCHAR(256) NULL
      ,weight DOUBLE NOT NULL DEFAULT 0
    )
    ;
