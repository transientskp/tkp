/**
 * This table contains the catalog sources that are associated.
 * Positions are weighted averages of the associated sources.
 * cattype:     'L': source exists in measurements
 *              'C': source exists in catalogsources
 *              'B': source exists in both
 */
CREATE SEQUENCE "seq_sourcelist" AS INTEGER;

CREATE TABLE sourcelist (
  srcid INT DEFAULT NEXT VALUE FOR "seq_sourcelist",
  src_name VARCHAR(50) NULL,
  zone INT NOT NULL,
  ra DOUBLE NOT NULL,
  decl DOUBLE NOT NULL,
  ra_err DOUBLE NOT NULL,
  decl_err DOUBLE NOT NULL,
  x DOUBLE NOT NULL,
  y DOUBLE NOT NULL,
  z DOUBLE NOT NULL,
  PRIMARY KEY (zone
              ,ra
              ,srcid
              ),
  UNIQUE (srcid)
);
