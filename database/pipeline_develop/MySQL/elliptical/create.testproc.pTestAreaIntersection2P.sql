DROP PROCEDURE IF EXISTS pTestAreaIntersection2P;

DELIMITER //

CREATE PROCEDURE pTestAreaIntersection2P(IN ie2_phi DOUBLE
                                  ,IN islope INT
                                  ,IN iC1_above BOOLEAN
                                  ,IN iC2_above BOOLEAN
                                  ,IN ie1_a DOUBLE
                                  ,IN ie1_b DOUBLE
                                  ,IN ie1_theta_0 DOUBLE
                                  ,IN ie1_theta_1 DOUBLE
                                  ,IN ic1_theta_0 DOUBLE
                                  ,IN ic1_theta_1 DOUBLE
                                  ,IN ie2_a DOUBLE
                                  ,IN ie2_b DOUBLE
                                  ,IN ie2_theta_1 DOUBLE
                                  ,IN ie2_theta_0 DOUBLE
                                  ,IN ic2_theta_1 DOUBLE
                                  ,IN ic2_theta_0 DOUBLE
                                  ,OUT ogeval INT
                                  ,OUT oe1_area DOUBLE
                                  ,OUT oe2_area DOUBLE
                                  ) 
BEGIN

  DECLARE e1_area, e2_area DOUBLE;
  /*DECLARE ogeval INT;*/

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

  SET oe1_area = e1_area;
  SET oe2_area = e2_area;

END;
//

DELIMITER ;
