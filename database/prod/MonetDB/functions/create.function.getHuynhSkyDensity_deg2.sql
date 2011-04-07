--DROP FUNCTION getHuynhSkyDensity_deg2;

/*
 */
CREATE FUNCTION getHuynhSkyDensity_deg2(ifreq DOUBLE
                                       ,iSnu_min DOUBLE
                                       ) RETURNS DOUBLE
BEGIN

  DECLARE a0, a1, a2, a3, a4, a5, a6 DOUBLE;
  DECLARE scale, Snu_first, fac1, sum, dSnu, mdSnu, Smax DOUBLE;
  DECLARE N, dN DOUBLE;
  DECLARE l, block INT;

  SET scale = POWER(ifreq / 1400, 0.7);
  SET N = 0;
  SET dN = 0;
  SET sum = 0;
  SET dSnu = 0;
  SET mdSnu = 0;
  SET Smax = 10;
  SET block = 0;
  SET a0 = 0.841;
  SET a1 = 0.540;
  SET a2 = 0.364;
  SET a3 = -0.063;
  SET a4 = -0.107;
  SET a5 = 0.052;
  SET a6 = -0.007;

  WHILE (mdSnu <= Smax) DO
    SET Snu_first = iSnu_min * POWER(10, block);
    SET dSnu = Snu_first / 10;
    SET mdSnu = Snu_first;
    SET l = 0;
    WHILE (l < 90 AND mdSnu <= Smax) DO
        SET fac1 = 1 / POWER(scale * mdSnu, 2.5);
        SET sum =   a0 * POWER(LOG10(scale * mdSnu * 1000), 0)
                  + a1 * POWER(LOG10(scale * mdSnu * 1000), 1)
                  + a2 * POWER(LOG10(scale * mdSnu * 1000), 2)
                  + a3 * POWER(LOG10(scale * mdSnu * 1000), 3)
                  + a4 * POWER(LOG10(scale * mdSnu * 1000), 4)
                  + a5 * POWER(LOG10(scale * mdSnu * 1000), 5)
                  + a6 * POWER(LOG10(scale * mdSnu * 1000), 6);
        SET dN = fac1 * POWER(10, sum) * scale * dSnu;
        IF mdSnu > iSnu_min / 3 THEN
            SET N = N + dN;
        END IF;
        SET mdSnu = mdSnu + dSnu;
        SET l = l + 1;
    END WHILE;
    SET block = block + 1;
  END WHILE;

  RETURN PI() * PI() * N / 32400;

END;

