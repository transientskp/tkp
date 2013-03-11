CREATE TABLE frequencyband
  (id SERIAL
  ,freq_central DOUBLE PRECISION DEFAULT NULL
  ,freq_low DOUBLE PRECISION DEFAULT NULL
  ,freq_high DOUBLE PRECISION DEFAULT NULL
{% ifdb postgresql %}
  ,PRIMARY KEY (id)
{% endifdb %}
  )
;

