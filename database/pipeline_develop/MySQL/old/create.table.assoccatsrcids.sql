/**
 * This is a in-memory table that contains all the collected 
 * ids of associated sources. It is solely used in the
 * procedure AssocSrc().
 */
CREATE TABLE assoccatsrcids (
  assoccatsrcid INT,
  UNIQUE INDEX (assoccatsrcid)
) ENGINE = MEMORY
;
