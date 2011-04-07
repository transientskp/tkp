/**
 */
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
