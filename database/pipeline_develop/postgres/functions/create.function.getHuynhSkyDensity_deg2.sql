--DROP FUNCTION getHuynhSkyDensity_deg2;

/*
 */
CREATE FUNCTION getHuynhSkyDensity_deg2(ifreq double precision
                                       ,iSnu_min double precision
                                       ) RETURNS double precision as $$
  DECLARE a0 double precision;
  declare a1 double precision;
  declare a2 double precision;
  declare a3 double precision;
  declare a4 double precision;
  declare a5 double precision;
  declare a6 double precision;
  DECLARE scale double precision;
  declare Snu_first double precision;
  declare fac1 double precision;
  declare sum double precision;
  declare dSnu double precision;
  declare mdSnu double precision;
  declare Smax double precision;
  DECLARE N double precision;
  declare dN double precision;
  DECLARE l int;
  declare block INT;
BEGIN

  scale := POWER(ifreq / 1400, 0.7);
  N := 0;
  dN := 0;
  sum := 0;
  dSnu := 0;
  mdSnu := 0;
  Smax := 10;
  block := 0;
  a0 := 0.841;
  a1 := 0.540;
  a2 := 0.364;
  a3 := -0.063;
  a4 := -0.107;
  a5 := 0.052;
  a6 := -0.007;

  WHILE (mdSnu <= Smax) loop
    Snu_first := iSnu_min * POWER(10, block);
    dSnu := Snu_first / 10;
    mdSnu := Snu_first;
    l := 0;
    WHILE (l < 90 AND mdSnu <= Smax) loop
        fac1 := 1 / POWER(scale * mdSnu, 2.5);
        sum :=   a0 * POWER(LOG10(scale * mdSnu * 1000), 0)
                  + a1 * POWER(LOG10(scale * mdSnu * 1000), 1)
                  + a2 * POWER(LOG10(scale * mdSnu * 1000), 2)
                  + a3 * POWER(LOG10(scale * mdSnu * 1000), 3)
                  + a4 * POWER(LOG10(scale * mdSnu * 1000), 4)
                  + a5 * POWER(LOG10(scale * mdSnu * 1000), 5)
                  + a6 * POWER(LOG10(scale * mdSnu * 1000), 6);
        dN := fac1 * POWER(10, sum) * scale * dSnu;
        IF mdSnu > iSnu_min / 3 THEN
            N := N + dN;
        END IF;
        mdSnu := mdSnu + dSnu;
        l := l + 1;
    END loop;
    block := block + 1;
  END loop;

  RETURN PI() * PI() * N / 32400;

END;
$$ language plpgsql;
