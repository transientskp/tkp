DROP FUNCTION IF EXISTS areaIntersection2P;

DELIMITER //

CREATE FUNCTION areaIntersection2P(ie2_phi DOUBLE
                                  ,islope INT
                                  ,iC1_above BOOLEAN
                                  ,iC2_above BOOLEAN
                                  ,ie1_a DOUBLE
                                  ,ie1_b DOUBLE
                                  ,ie1_theta_0 DOUBLE
                                  ,ie1_theta_1 DOUBLE
                                  ,ic1_theta_0 DOUBLE
                                  ,ic1_theta_1 DOUBLE
                                  ,ie2_a DOUBLE
                                  ,ie2_b DOUBLE
                                  ,ie2_theta_1 DOUBLE
                                  ,ie2_theta_0 DOUBLE
                                  ,ic2_theta_1 DOUBLE
                                  ,ic2_theta_0 DOUBLE
                                  ) RETURNS DOUBLE
DETERMINISTIC
BEGIN

  DECLARE e1_area, e2_area DOUBLE;
  DECLARE ogeval INT;

  IF ie2_phi >= 0 THEN
    IF islope >= 0 THEN
      IF iC2_above = TRUE THEN
        IF ie1_theta_0 < 0 THEN
          /*piab - (P0->P1)*/
          SET ogeval = 1;
          SET e1_area = complementAreaLineEllipticalArc(ie1_a,ie1_b,ie1_theta_0,ie1_theta_1,ic1_theta_0,ic1_theta_1);
          SET e2_area = complementAreaLineEllipticalArc(ie2_a,ie2_b,ie2_theta_1,ie2_theta_0,ic2_theta_1,ic2_theta_0);
        ELSE
          /*P0->P1*/
          SET ogeval = 2;
          SET e1_area = areaLineEllipticalArc(ie1_a,ie1_b,ie1_theta_0,ie1_theta_1,ic1_theta_0,ic1_theta_1);
          SET e2_area = areaLineEllipticalArc(ie2_a,ie2_b,ie2_theta_1,ie2_theta_0,ic2_theta_1,ic2_theta_0);
        END IF;
      ELSE
        IF ie1_theta_0 < 0 THEN
          /*P0->P1*/
          SET ogeval = 3;
          SET e1_area = areaLineEllipticalArc(ie1_a,ie1_b,ie1_theta_0,ie1_theta_1,ic1_theta_0,ic1_theta_1);
          SET e2_area = areaLineEllipticalArc(ie2_a,ie2_b,ie2_theta_1,ie2_theta_0,ic2_theta_1,ic2_theta_0);
        ELSE
          /*piab - (P0->P1)*/
          SET ogeval = 4;
          SET e1_area = complementAreaLineEllipticalArc(ie1_a,ie1_b,ie1_theta_0,ie1_theta_1,ic1_theta_0,ic1_theta_1);
          SET e2_area = complementAreaLineEllipticalArc(ie2_a,ie2_b,ie2_theta_1,ie2_theta_0,ic2_theta_1,ic2_theta_0);
        END IF;
      END IF;
    ELSE
      IF iC1_above = TRUE THEN
        IF ie1_theta_1 < 0 THEN
          /*P0->P1*/
          SET ogeval = 5;
          SET e1_area = areaLineEllipticalArc(ie1_a,ie1_b,ie1_theta_0,ie1_theta_1,ic1_theta_0,ic1_theta_1);
          SET e2_area = areaLineEllipticalArc(ie2_a,ie2_b,ie2_theta_1,ie2_theta_0,ic2_theta_1,ic2_theta_0);
        ELSE
          /*piab - (P0->P1)*/
          SET ogeval = 6;
          SET e1_area = complementAreaLineEllipticalArc(ie1_a,ie1_b,ie1_theta_0,ie1_theta_1,ic1_theta_0,ic1_theta_1);
          SET e2_area = complementAreaLineEllipticalArc(ie2_a,ie2_b,ie2_theta_1,ie2_theta_0,ic2_theta_1,ic2_theta_0);
        END IF;
      ELSE
        /*P0->P1*/
        SET ogeval = 7;
        SET e1_area = areaLineEllipticalArc(ie1_a,ie1_b,ie1_theta_0,ie1_theta_1,ic1_theta_0,ic1_theta_1);
        SET e2_area = areaLineEllipticalArc(ie2_a,ie2_b,ie2_theta_1,ie2_theta_0,ic2_theta_1,ic2_theta_0);
      END IF;
    END IF;
  ELSE
    IF islope >= 0 THEN
      IF iC1_above = TRUE THEN
        /*P0->P1*/
        SET ogeval = 8;
        SET e1_area = areaLineEllipticalArc(ie1_a,ie1_b,ie1_theta_0,ie1_theta_1,ic1_theta_0,ic1_theta_1);
        SET e2_area = areaLineEllipticalArc(ie2_a,ie2_b,ie2_theta_1,ie2_theta_0,ic2_theta_1,ic2_theta_0);
      ELSE
        IF ie1_theta_0 > 0 THEN
          /*P0->P1*/
          SET ogeval = 9;
          SET e1_area = areaLineEllipticalArc(ie1_a,ie1_b,ie1_theta_0,ie1_theta_1,ic1_theta_0,ic1_theta_1);
          SET e2_area = areaLineEllipticalArc(ie2_a,ie2_b,ie2_theta_1,ie2_theta_0,ic2_theta_1,ic2_theta_0);
        ELSE
          /*piab - (P0->P1)*/
          SET ogeval = 10;
          SET e1_area = complementAreaLineEllipticalArc(ie1_a,ie1_b,ie1_theta_0,ie1_theta_1,ic1_theta_0,ic1_theta_1);
          SET e2_area = complementAreaLineEllipticalArc(ie2_a,ie2_b,ie2_theta_1,ie2_theta_0,ic2_theta_1,ic2_theta_0);
        END IF;
      END IF;
    ELSE
      IF iC2_above = TRUE THEN
        IF ie1_theta_1 < 0 THEN
          /*piab - (P0->P1)*/
          SET ogeval = 11;
          SET e1_area = complementAreaLineEllipticalArc(ie1_a,ie1_b,ie1_theta_0,ie1_theta_1,ic1_theta_0,ic1_theta_1);
          SET e2_area = complementAreaLineEllipticalArc(ie2_a,ie2_b,ie2_theta_1,ie2_theta_0,ic2_theta_1,ic2_theta_0);
        ELSE
          /*P0->P1*/
          SET ogeval = 12;
          SET e1_area = areaLineEllipticalArc(ie1_a,ie1_b,ie1_theta_0,ie1_theta_1,ic1_theta_0,ic1_theta_1);
          SET e2_area = areaLineEllipticalArc(ie2_a,ie2_b,ie2_theta_1,ie2_theta_0,ic2_theta_1,ic2_theta_0);
        END IF;
      ELSE
        IF ie1_theta_1 < 0 THEN
          /*P0->P1*/
          SET ogeval = 13;
          SET e1_area = areaLineEllipticalArc(ie1_a,ie1_b,ie1_theta_0,ie1_theta_1,ic1_theta_0,ic1_theta_1);
          SET e2_area = areaLineEllipticalArc(ie2_a,ie2_b,ie2_theta_1,ie2_theta_0,ic2_theta_1,ic2_theta_0);
        ELSE
          /*piab - (P0->P1)*/
          SET ogeval = 14;
          SET e1_area = complementAreaLineEllipticalArc(ie1_a,ie1_b,ie1_theta_0,ie1_theta_1,ic1_theta_0,ic1_theta_1);
          SET e2_area = complementAreaLineEllipticalArc(ie2_a,ie2_b,ie2_theta_1,ie2_theta_0,ic2_theta_1,ic2_theta_0);
        END IF;
      END IF;
    END IF;
  END IF;

  RETURN (e1_area + e2_area);

END;
//

DELIMITER ;
