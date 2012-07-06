/**
 * This table keeps track of the versions and changes
 */
CREATE SEQUENCE "seq_version" AS INTEGER;

CREATE TABLE version
  ("name" VARCHAR(12) NOT NULL
  ,"value" INT NOT NULL
  ,PRIMARY KEY ("name")
  )
;

INSERT INTO version ("name", "value") VALUES ('revision', 1);


