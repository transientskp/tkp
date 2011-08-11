/**
 * This table contains the detected transients and their characteristics
 */
CREATE SEQUENCE "seq_transients" AS INTEGER;

CREATE TABLE "transients" (
	"transientid"      int           DEFAULT next value for "seq_transients",
	"xtrsrc_id"        int           NOT NULL,
	"siglevel"         double        DEFAULT 0,
        "detection_level"  double        DEFAULT 0,
	"status"           int           DEFAULT 0,
	"t_start"          TIMESTAMP
);
