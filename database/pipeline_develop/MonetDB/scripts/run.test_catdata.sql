USE pipeline_test;

SELECT NOW();

CALL test_load_catdata();

SELECT NOW();

CALL test_assoc_catdata();

SELECT NOW();
