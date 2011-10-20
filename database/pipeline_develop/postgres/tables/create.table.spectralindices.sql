/**
 */
CREATE TABLE spectralindices 
  (spindxid SERIAL PRIMARY KEY
  ,catsrc_id INT NOT NULL
  ,spindx_degree INT NOT NULL DEFAULT 0
  ,c0 double precision NOT NULL DEFAULT 0
  ,c1 double precision NULL DEFAULT 0
  ,c2 double precision NULL DEFAULT 0
  ,c3 double precision NULL DEFAULT 0
  ,c4 double precision NULL DEFAULT 0
  ,c5 double precision NULL DEFAULT 0
  ,FOREIGN KEY (catsrc_id) REFERENCES catalogedsources (catsrcid)
  )
;
