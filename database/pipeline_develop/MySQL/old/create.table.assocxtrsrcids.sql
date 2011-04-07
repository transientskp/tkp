/**
 * This is a in-memory table that contains all the collected 
 * ids of associated sources. It is solely used in the
 * procedure AssocSrc().
 */
CREATE TABLE assocxtrsrcids (
  assocxtrsrcid INT,
  UNIQUE INDEX (assocxtrsrcid)
) ENGINE = MEMORY
;
