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

{% ifdb postgresql %}
AS $$
  DECLARE nskyrgn INT;
  DECLARE oskyrgnid INT;
  DECLARE dummy DOUBLE PRECISION;
BEGIN

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
  	RETURNING id into oskyrgnid
    ;

  SELECT updateSkyRgnMembers(oskyrgnid)
  	INTO dummy;
    
  END IF;

  RETURN oskyrgnid;

END;

$$ LANGUAGE plpgsql;
{% endifdb %}



{% ifdb monetdb %}
BEGIN

  DECLARE nskyrgn INT;
  DECLARE oskyrgnid INT;

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
    SELECT NEXT VALUE FOR seq_skyregion INTO oskyrgnid;

    INSERT INTO skyregion
      (id
      ,dataset
      ,centre_ra
      ,centre_decl
      ,xtr_radius
      ,x
      ,y
      ,z
      )
    SELECT oskyrgnid
	      ,idataset
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

  DECLARE dummy DOUBLE;
  SELECT updateSkyRgnMembers(oskyrgnid)
  	INTO dummy;

  END IF;

  RETURN oskyrgnid;

END;
{% endifdb %}