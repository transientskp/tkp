USE pipeline_test;

SELECT NOW();

CALL test_load_simdata();

SELECT NOW();

CALL test_assoc_simdata();

SELECT NOW();
