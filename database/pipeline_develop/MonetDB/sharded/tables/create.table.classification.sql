/**
 * This table contains classification of transients
 */
CREATE TABLE "classification" (
	"transient_id"   int           NOT NULL,
	"classification" varchar(256),
	"weight"         double        NOT NULL        DEFAULT 0
);
