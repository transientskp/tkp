DROP PROCEDURE IF EXISTS SortAngles;

DELIMITER //

/**
 * This procedure sorts the input points, so that 
 * the sequence is ordered from -pi -> pi
 */
CREATE PROCEDURE SortAngles(IN itheta_0 DOUBLE
                           ,IN itheta_1 DOUBLE
                           ,IN itheta_2 DOUBLE
                           ,IN itheta_3 DOUBLE
                           ,IN iP0_x DOUBLE
                           ,IN iP0_y DOUBLE
                           ,IN iP1_x DOUBLE
                           ,IN iP1_y DOUBLE
                           ,IN iP2_x DOUBLE
                           ,IN iP2_y DOUBLE
                           ,IN iP3_x DOUBLE
                           ,IN iP3_y DOUBLE
                           ,OUT oalpha_0 DOUBLE
                           ,OUT oalpha_1 DOUBLE
                           ,OUT oalpha_2 DOUBLE
                           ,OUT oalpha_3 DOUBLE
                           ,OUT oQ0_x DOUBLE
                           ,OUT oQ0_y DOUBLE
                           ,OUT oQ1_x DOUBLE
                           ,OUT oQ1_y DOUBLE
                           ,OUT oQ2_x DOUBLE
                           ,OUT oQ2_y DOUBLE
                           ,OUT oQ3_x DOUBLE
                           ,OUT oQ3_y DOUBLE
                           ) 
BEGIN

  DECLARE alpha_0,alpha_1,alpha_2,alpha_3,alpha_swap DOUBLE;
  DECLARE Q0_x,Q0_y,Q1_x,Q1_y,Q2_x,Q2_y,Q3_x,Q3_y,Qswap_x,Qswap_y DOUBLE;
  DECLARE i INT;

  SET alpha_0 = itheta_0;
  SET alpha_1 = itheta_1;
  SET alpha_2 = itheta_2;
  SET alpha_3 = itheta_3;

  SET Q0_x = iP0_x;
  SET Q0_y = iP0_y;
  SET Q1_x = iP1_x;
  SET Q1_y = iP1_y;
  SET Q2_x = iP2_x;
  SET Q2_y = iP2_y;
  SET Q3_x = iP3_x;
  SET Q3_y = iP3_y;

  SET i = 0;
  WHILE (i < 4) DO
    IF alpha_0 > alpha_1 THEN
      SET alpha_swap = alpha_1;
      SET alpha_1 = alpha_0;
      SET alpha_0 = alpha_swap;
      SET Qswap_x = Q1_x;
      SET Q1_x = Q0_x;
      SET Q0_x = Qswap_x;
      SET Qswap_y = Q1_y;
      SET Q1_y = Q0_y;
      SET Q0_y = Qswap_y;
    END IF;
    IF alpha_1 > alpha_2 THEN
      SET alpha_swap = alpha_2;
      SET alpha_2 = alpha_1;
      SET alpha_1 = alpha_swap;
      SET Qswap_x = Q2_x;
      SET Q2_x = Q1_x;
      SET Q1_x = Qswap_x;
      SET Qswap_y = Q2_y;
      SET Q2_y = Q1_y;
      SET Q1_y = Qswap_y;
    END IF;
    IF alpha_2 > alpha_3 THEN
      SET alpha_swap = alpha_3;
      SET alpha_3 = alpha_2;
      SET alpha_2 = alpha_swap;
      SET Qswap_x = Q3_x;
      SET Q3_x = Q2_x;
      SET Q2_x = Qswap_x;
      SET Qswap_y = Q3_y;
      SET Q3_y = Q2_y;
      SET Q2_y = Qswap_y;
    END IF;
    SET i = i + 1;
  END WHILE;

  SET oalpha_0 = alpha_0;
  SET oalpha_1 = alpha_1;
  SET oalpha_2 = alpha_2;
  SET oalpha_3 = alpha_3;

  SET oQ0_x = Q0_x;
  SET oQ0_y = Q0_y;
  SET oQ1_x = Q1_x;
  SET oQ1_y = Q1_y;
  SET oQ2_x = Q2_x;
  SET oQ2_y = Q2_y;
  SET oQ3_x = Q3_x;
  SET oQ3_y = Q3_y;

END;
//

DELIMITER ;

