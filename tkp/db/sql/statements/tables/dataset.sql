{% ifdb monetdb %}
CREATE SEQUENCE seq_dataset AS INTEGER;
CREATE TABLE dataset
  (id INTEGER NOT NULL DEFAULT NEXT VALUE FOR seq_dataset
{% endifdb %}


{% ifdb postgresql %}
CREATE TABLE dataset
  (id SERIAL
{% endifdb %}

  ,rerun INT NOT NULL DEFAULT '0'
  ,"type" SMALLINT NOT NULL DEFAULT 1
  ,process_ts TIMESTAMP NOT NULL
  ,detection_threshold DOUBLE PRECISION NULL
  ,analysis_threshold DOUBLE PRECISION NULL
  ,assoc_radius DOUBLE PRECISION NULL
  ,backsize_x SMALLINT NULL
  ,backsize_y SMALLINT NULL
  ,margin_width DOUBLE PRECISION NULL
  ,description VARCHAR(100) NOT NULL
  ,node SMALLINT NOT NULL DEFAULT %NODE%
  ,nodes SMALLINT NOT NULL DEFAULT %NODES%
  ,PRIMARY KEY (id)
  )
;

