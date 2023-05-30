{% if db.engine == 'postgresql' %}
{% if db.version is none or db.version < 14 %}
/*
  Defines 'median' aggregate function, cf.
  https://wiki.postgresql.org/wiki/Aggregate_Median
*/

CREATE FUNCTION _final_median(anyarray) RETURNS float8 AS $$
  WITH q AS
  (
     SELECT val
     FROM unnest($1) val
     WHERE VAL IS NOT NULL
     ORDER BY 1
  ),
  cnt AS
  (
    SELECT COUNT(*) AS c FROM q
  )
  SELECT AVG(val)::float8
  FROM
  (
    SELECT val FROM q
    LIMIT  2 - MOD((SELECT c FROM cnt), 2)
    OFFSET GREATEST(CEIL((SELECT c FROM cnt) / 2.0) - 1,0)
  ) q2;
$$ LANGUAGE sql IMMUTABLE;

CREATE AGGREGATE median(anyelement) (
  SFUNC=array_append,
  STYPE=anyarray,
  FINALFUNC=_final_median,
  INITCOND='{}'
);

{% else %}

/*
  Defines 'median' aggregate function, cf.
  https://wiki.postgresql.org/wiki/Aggregate_Median
*/

CREATE FUNCTION _final_median(anycompatiblearray) RETURNS float8 AS $$
  WITH q AS
  (
     SELECT val
     FROM unnest($1) val
     WHERE VAL IS NOT NULL
     ORDER BY 1
  ),
  cnt AS
  (
    SELECT COUNT(*) AS c FROM q
  )
  SELECT AVG(val)::float8
  FROM
  (
    SELECT val FROM q
    LIMIT  2 - MOD((SELECT c FROM cnt), 2)
    OFFSET GREATEST(CEIL((SELECT c FROM cnt) / 2.0) - 1,0)
  ) q2;
$$ LANGUAGE sql IMMUTABLE;

CREATE AGGREGATE median(anycompatible) (
  SFUNC=array_append,
  STYPE=anycompatiblearray,
  FINALFUNC=_final_median,
  INITCOND='{}'
);

{% endif %}
{% endif %}
