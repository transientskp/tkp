{% ifdb monetdb %}
CREATE FUNCTION least(v1 DOUBLE, v2 DOUBLE)
RETURNS DOUBLE
LANGUAGE PYTHON {

    import numpy
    return numpy.amin([v1, v2])

};

{% endifdb %}

-- a query file can't be empty (which is the case for postgresql)
select 1;
