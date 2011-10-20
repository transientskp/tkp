/**
 * This table contains the detected transients and their characteristics
 */
CREATE TABLE "transients" (
	"transientid"      SERIAL,
	"xtrsrc_id"        int           NOT NULL,
	"siglevel"         double precision DEFAULT 0,
        "detection_level"  double precision DEFAULT 0,
	"status"           int           DEFAULT 0,
	"t_start"          TIMESTAMP
);
