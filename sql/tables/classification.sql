/**
 * This table contains classification of transients
 */
CREATE TABLE classification
	( transient_id INTEGER NOT NULL
	,classification VARCHAR(256)
	,weight DOUBLE NOT NULL DEFAULT 0
);  
