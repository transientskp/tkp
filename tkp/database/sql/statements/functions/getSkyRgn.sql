--DROP FUNCTION getSkyRgn;

/*
 * This function gets an id for a skyregion,
 * given a pair of central co-ordinates and a radius.
 * 
 * If no matching skyregion is found, a new one is inserted. 
 * In this case we also trigger execution of `updateSkyRgnMembers` for the new
 * skyregion - this performs a simple assocation with current members of the
 * runningcatalog to find sources that should be visible in the new skyregion,
 * and updates the assocskyrgn table accordingly.
 */

CREATE FUNCTION getSkyRgn(idataset INTEGER, icentre_ra DOUBLE PRECISION,
                          icentre_decl DOUBLE PRECISION,
                          ixtr_radius DOUBLE PRECISION)
RETURNS INT

{% ifdb monetdb %}
BEGIN
  DECLARE nskyrgn INT;
  DECLARE oskyrgnid INT;
  DECLARE dummy DOUBLE PRECISION;
{% endifdb %}

{% ifdb postgresql %}
AS $$
  DECLARE nskyrgn INT;
  DECLARE oskyrgnid INT;
  DECLARE dummy DOUBLE PRECISION;
BEGIN
{% endifdb %}

  SELECT COUNT(*)
    INTO nskyrgn
    FROM skyregion
   WHERE dataset = idataset
     AND centre_ra = icentre_ra
     AND centre_decl = icentre_decl
     AND xtr_radius = ixtr_radius 
  ;

  IF nskyrgn = 1 THEN
    SELECT id
      INTO oskyrgnid
      FROM skyregion
     WHERE dataset = idataset
	   AND centre_ra = icentre_ra
	   AND centre_decl = icentre_decl
	   AND xtr_radius = ixtr_radius 
    ;
  ELSE

    INSERT INTO skyregion
      (dataset
      ,centre_ra
      ,centre_decl
      ,xtr_radius
      ,x
      ,y
      ,z
      ) 
    SELECT idataset
	      ,icentre_ra
	      ,icentre_decl
	      ,ixtr_radius
	      ,cart.x
	      ,cart.y
	      ,cart.z
    FROM (SELECT *
		  FROM cartesian(icentre_ra,icentre_decl)
		  ) cart
    ;
  oskyrgnid := lastval();

  SELECT updateSkyRgnMembers(oskyrgnid)
  	INTO dummy;
    
  END IF;

  RETURN oskyrgnid;

END;

{% ifdb postgresql %}
$$ LANGUAGE plpgsql;
{% endifdb %}