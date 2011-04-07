-----------------------------------------------------------------------
SET @testcase = '(1) Q3 -> Q3';
-----------------------------------------------------------------------

/**
 * We assume a = 4, b = 3, center=(0,0)
 */

/** 
 * P0 at theta_0 in Q3 => branch k = -1
 * P1 at theta_1 in Q3 => branch k = -1
 * no neg. y_crossing
 */
SET @theta_0 = -180 + 20;
SET @theta_1 = -180 + 70;
SET @crossing = FALSE;

SELECT @testcase
      ,@theta_0
      ,@theta_1
      ,@crossing
      ,PI() * 3 * 4 AS EllipseArea
      ,(3 * 4 / 2)
       * (
            (ATAN(4*TAN(RADIANS(@theta_1)) / 3) - PI()) 
          - (ATAN(4*TAN(RADIANS(@theta_0)) / 3) - PI())
         ) AS 'SectorArea'
      ,(3 * 4 / 2)
       * (
            (ATAN(4*TAN(RADIANS(@theta_1)) / 3) - PI()) 
          - (ATAN(4*TAN(RADIANS(@theta_0)) / 3) - PI())
         ) 
       / (PI() * 4 * 3) AS 'Fraction'
      ,areaOfEllipticalSector(4/3600,3/3600,@theta_0,@theta_1) 
       AS 'SectorArea from f()'
;

-----------------------------------------------------------------------
SET @testcase = '(2) Q3 -> Q4';
-----------------------------------------------------------------------

/**
 * P0 at same theta_0 in Q3, k = -1
 * P1 at theta_1 in Q4 => branch k = 0
 * neg. y_crossing
 * Arc crosses neg. y-axis, thus we set theta_1 = theta_1 + 2pi in tan()
 */
SET @theta_1 = @theta_1 + 90;
SET @crossing = TRUE;

SELECT @testcase
      ,@theta_0
      ,@theta_1
      ,@crossing
      ,PI() * 3 * 4 AS EllipseArea
      ,(3 * 4 / 2)
       * (
            (ATAN(4*TAN(RADIANS(@theta_1 + 360)) / 3) ) 
          - (ATAN(4*TAN(RADIANS(@theta_0)) / 3) - PI())
         ) AS 'SectorArea'
      ,(3 * 4 / 2)
       * (
            (ATAN(4*TAN(RADIANS(@theta_1 + 360)) / 3) ) 
          - (ATAN(4*TAN(RADIANS(@theta_0)) / 3) - PI())
         ) 
       / (PI() * 4 * 3) AS 'Fraction'
      ,areaOfEllipticalSector(4/3600,3/3600,@theta_0,@theta_1) 
       AS 'SectorArea from f()'
;

-----------------------------------------------------------------------
SET @testcase = '(3) Q3 -> Q1';
-----------------------------------------------------------------------

/**
 * P0 at same theta_0 in Q3, k = -1
 * P1 at theta_1 in Q1 => branch k = 0
 * neg. y_crossing
 * Arc crosses neg. y-axis, thus we set theta_1 = theta_1 + 2pi in tan()
 */
SET @theta_1 = @theta_1 + 90;
SET @crossing = TRUE;

SELECT @testcase
      ,@theta_0
      ,@theta_1
      ,@crossing
      ,PI() * 3 * 4 AS EllipseArea
      ,(3 * 4 / 2)
       * (
            (ATAN(4*TAN(RADIANS(@theta_1 + 360)) / 3) ) 
          - (ATAN(4*TAN(RADIANS(@theta_0)) / 3) - PI())
         ) AS 'SectorArea'
      ,(3 * 4 / 2)
       * (
            (ATAN(4*TAN(RADIANS(@theta_1 + 360)) / 3) ) 
          - (ATAN(4*TAN(RADIANS(@theta_0)) / 3) - PI())
         ) 
       / (PI() * 4 * 3) AS 'Fraction'
      ,areaOfEllipticalSector(4/3600,3/3600,@theta_0,@theta_1) 
       AS 'SectorArea from f()'
;

-----------------------------------------------------------------------
SET @testcase = '(4) Q3 -> Q2';
-----------------------------------------------------------------------

/**
 * P0 at same theta_0 in Q3, k = -1
 * P1 at theta_1 in Q2 => branch k = 1
 * neg. y_crossing
 * Arc crosses neg. y-axis, thus we set theta_1 = theta_1 + 2pi in tan()
 */
SET @theta_1 = @theta_1 + 90;
SET @crossing = TRUE;

SELECT @testcase
      ,@theta_0
      ,@theta_1
      ,@crossing
      ,PI() * 3 * 4 AS EllipseArea
      ,(3 * 4 / 2)
       * (
            (ATAN(4*TAN(RADIANS(@theta_1 + 360)) / 3) + PI()) 
          - (ATAN(4*TAN(RADIANS(@theta_0)) / 3) - PI())
         ) AS 'SectorArea'
      ,(3 * 4 / 2)
       * (
            (ATAN(4*TAN(RADIANS(@theta_1 + 360)) / 3) + PI()) 
          - (ATAN(4*TAN(RADIANS(@theta_0)) / 3) - PI())
         ) 
       / (PI() * 4 * 3) AS 'Fraction'
      ,areaOfEllipticalSector(4/3600,3/3600,@theta_0,@theta_1) 
       AS 'SectorArea from f()'
;

-----------------------------------------------------------------------
SET @testcase = '(5) Q3 -> Q4Q1Q2Q3';
-----------------------------------------------------------------------

/**
 * P0 at same theta_0 in Q3, k = -1
 * P1 at theta_1 in Q3, but smaller than theta_0 => branch k = -1
 * neg. y_crossing
 * Arc crosses neg. y-axis, thus we set theta_1 = theta_1 + 2pi in tan()
 */
SET @theta_1 = -170;
SET @crossing = TRUE;

SELECT @testcase
      ,@theta_0
      ,@theta_1
      ,@crossing
      ,PI() * 3 * 4 AS EllipseArea
      ,PI() * 3 * 4 
       -
       (3 * 4 / 2)
       * (
            (ATAN(4*TAN(RADIANS(@theta_1 + 360)) / 3) - PI()) 
          - (ATAN(4*TAN(RADIANS(@theta_0)) / 3) - PI())
         ) AS 'Alt_SectorArea'
      ,(3 * 4 / 2)
       * (
            (ATAN(4*TAN(RADIANS(@theta_1 + 360)) / 3) - PI()) 
          - (ATAN(4*TAN(RADIANS(@theta_0)) / 3) - PI())
         ) AS 'SectorArea'
      ,(3 * 4 / 2)
       * (
            (ATAN(4*TAN(RADIANS(@theta_1 + 360)) / 3) - PI()) 
          - (ATAN(4*TAN(RADIANS(@theta_0)) / 3) - PI())
         ) 
       / (PI() * 4 * 3) AS 'Fraction'
      ,areaOfEllipticalSector(4/3600,3/3600,@theta_0,@theta_1) 
       AS 'SectorArea from f()'
;

-----------------------------------------------------------------------
SET @testcase = '(6) Q4 -> Q4';
-----------------------------------------------------------------------

/**
 * P0 at theta_0 in Q4 => branch k = 0
 * P1 at theta_1 in Q4 => branch k = 0
 * no neg. y_crossing
 */
SET @theta_0 = -180 + 20 + 90;
SET @theta_1 = -180 + 70 + 90;
SET @crossing = FALSE;

SELECT @testcase
      ,@theta_0
      ,@theta_1
      ,@crossing
      ,PI() * 3 * 4 AS EllipseArea
      ,(3 * 4 / 2)
       * (
            (ATAN(4*TAN(RADIANS(@theta_1)) / 3) ) 
          - (ATAN(4*TAN(RADIANS(@theta_0)) / 3) )
         ) AS 'SectorArea'
      ,(3 * 4 / 2)
       * (
            (ATAN(4*TAN(RADIANS(@theta_1)) / 3) ) 
          - (ATAN(4*TAN(RADIANS(@theta_0)) / 3) )
         ) 
       / (PI() * 4 * 3) AS 'Fraction'
      ,areaOfEllipticalSector(4/3600,3/3600,@theta_0,@theta_1) 
       AS 'SectorArea from f()'
;

-----------------------------------------------------------------------
SET @testcase = '(7) Q4 -> Q1';
-----------------------------------------------------------------------

/**
 * P0 at same theta_0,  in Q4, branch k = 0
 * P1 at theta_1 in Q1 => branch k = 0
 * no neg. y_crossing
 */
SET @theta_1 = @theta_1 + 90;
SET @crossing = FALSE;

SELECT @testcase
      ,@theta_0
      ,@theta_1
      ,@crossing
      ,PI() * 3 * 4 AS EllipseArea
      ,(3 * 4 / 2)
       * (
            (ATAN(4*TAN(RADIANS(@theta_1)) / 3) ) 
          - (ATAN(4*TAN(RADIANS(@theta_0)) / 3) )
         ) AS 'SectorArea'
      ,(3 * 4 / 2)
       * (
            (ATAN(4*TAN(RADIANS(@theta_1)) / 3) ) 
          - (ATAN(4*TAN(RADIANS(@theta_0)) / 3) )
         ) 
       / (PI() * 4 * 3) AS 'Fraction'
      ,areaOfEllipticalSector(4/3600,3/3600,@theta_0,@theta_1) 
       AS 'SectorArea from f()'
;

-----------------------------------------------------------------------
SET @testcase = '(8) Q4 -> Q2';
-----------------------------------------------------------------------

/**
 * P0 at same theta_0,  in Q4, branch k = 0
 * P1 at theta_1 in Q2 => branch k = 1
 * no neg. y_crossing
 */
SET @theta_1 = @theta_1 + 90;
SET @crossing = FALSE;

SELECT @testcase
      ,@theta_0
      ,@theta_1
      ,@crossing
      ,PI() * 3 * 4 AS EllipseArea
      ,(3 * 4 / 2)
       * (
            (ATAN(4*TAN(RADIANS(@theta_1)) / 3) + PI()) 
          - (ATAN(4*TAN(RADIANS(@theta_0)) / 3) )
         ) AS 'SectorArea'
      ,(3 * 4 / 2)
       * (
            (ATAN(4*TAN(RADIANS(@theta_1)) / 3) + PI()) 
          - (ATAN(4*TAN(RADIANS(@theta_0)) / 3) )
         ) 
       / (PI() * 4 * 3) AS 'Fraction'
      ,areaOfEllipticalSector(4/3600,3/3600,@theta_0,@theta_1) 
       AS 'SectorArea from f()'
;


