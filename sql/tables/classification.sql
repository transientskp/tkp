/**
 * This table contains classification of transients
 *
 * TODO: evert's tabel, how should we handle this? what is the ID?
 */

CREATE TABLE classification
	( transient_id INTEGER NOT NULL
	,classification VARCHAR(256)
	,weight DOUBLE NOT NULL DEFAULT 0
);  
