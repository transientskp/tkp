DROP PROCEDURE IF EXISTS InitAssoc_Classification;

DELIMITER //

/**
 * This procedure initialises the assoc_classification table.
 */
CREATE PROCEDURE InitAssoc_Classification()
BEGIN

  DELETE FROM assoc_classification;

  INSERT INTO assoc_classification 
    (assoc_classid
    ,type
    ,assoc_class
    ,description
    ) VALUES 
    (    0, 0, 'U', 'Unknown source'),
    (    1, 1, 'S', 'Single component source'),
    (    2, 2, 'M', 'Multicomponent source'),
    (    3, 3, 'C', 'Component of a multicomponent source'),
    (    4, 4, 'E', 'Extended source (more than four components)'),
    (    5, 5, 'U', 'Unknown'),
    (   10, 1, 'AE1', 'Associated to extractedsource'),
    (   11, 1, 'AE2', 'Associated to extractedsource (2sigma)'),
    (   12, 1, 'AE3', 'Associated to extractedsource (3sigma)'),
    (   20, 1, 'AME1', 'Associated to multiple extractedsources'),
    (   21, 1, 'AME2', 'Associated to multiple extractedsources (2sigma)'),
    (   22, 1, 'AME2', 'Associated to multiple extractedsources (3sigma)'),
    ( 1000, 1, 'AC1', 'Associated to catalguesource'),
    ( 1010, 1, 'AC1AE1', 'AC1 + AE1'),
    ( 1011, 1, 'AC1AE2', 'AC1 + AE2'),
    ( 1012, 1, 'AC1AE3', 'AC1 + AE3'),
    ( 1020, 1, 'AC1AME1', 'AC1 + AME1'),
    ( 1021, 1, 'AC1AME2', 'AC1 + AME2'),
    ( 1022, 1, 'AC1AME3', 'AC1 + AME3'),
    ( 1100, 1, 'AC2', 'Associated to catalguesource (2sigma)'),
    ( 1110, 1, 'AC2AE1', 'AC2 + AE1'),
    ( 1111, 1, 'AC2AE2', 'AC2 + AE2'),
    ( 1112, 1, 'AC2AE3', 'AC2 + AE3'),
    ( 1120, 1, 'AC2AME1', 'AC2 + AME1'),
    ( 1121, 1, 'AC2AME2', 'AC2 + AME2'),
    ( 1122, 1, 'AC2AME3', 'AC2 + AME3'),
    ( 1200, 1, 'AC3', 'Associated to catalguesource (3sigma)'),
    ( 1210, 1, 'AC3AE1', 'AC3 + AE1'),
    ( 1211, 1, 'AC3AE2', 'AC3 + AE2'),
    ( 1212, 1, 'AC3AE3', 'AC3 + AE3'),
    ( 1220, 1, 'AC3AME1', 'AC3 + AME1'),
    ( 1221, 1, 'AC3AME2', 'AC3 + AME2'),
    ( 1222, 1, 'AC3AME3', 'AC3 + AME3'),
    ( 2000, 1, 'AMC1', 'Associated to multiple catalguesources'),
    ( 2010, 1, 'AMC1AE1', 'AMC1 + AE1'),
    ( 2011, 1, 'AMC1AE2', 'AMC1 + AE2'),
    ( 2012, 1, 'AMC1AE3', 'AMC1 + AE3'),
    ( 2020, 1, 'AMC1AME1', 'AMC1 + AME1'),
    ( 2021, 1, 'AMC1AME2', 'AMC1 + AME2'),
    ( 2022, 1, 'AMC1AME3', 'AMC1 + AME3'),
    ( 2100, 1, 'AMC2', 'Associated to multiple catalguesources (2sigma)'),
    ( 2110, 1, 'AMC2AE1', 'AMC2 + AE1'),
    ( 2111, 1, 'AMC2AE2', 'AMC2 + AE2'),
    ( 2112, 1, 'AMC2AE3', 'AMC2 + AE3'),
    ( 2120, 1, 'AMC2AME1', 'AMC2 + AME1'),
    ( 2121, 1, 'AMC2AME2', 'AMC2 + AME2'),
    ( 2122, 1, 'AMC2AME3', 'AMC2 + AME3'),
    ( 2200, 1, 'AMC3', 'Associated to multiple catalguesources (3sigma)'),
    ( 2210, 1, 'AMC3AE1', 'AMC3 + AE1'),
    ( 2211, 1, 'AMC3AE2', 'AMC3 + AE2'),
    ( 2212, 1, 'AMC3AE3', 'AMC3 + AE3'),
    ( 2220, 1, 'AMC3AME1', 'AMC3 + AME1'), 
    ( 2221, 1, 'AMC3AME2', 'AMC3 + AME2'),
    ( 2222, 1, 'AMC3AME3', 'AMC3 + AME3')
  ;

END;
//

DELIMITER ;
