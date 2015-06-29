{% ifdb monetdb %}
CALL BuildFrequencyBands();
{% endifdb %}

{% ifdb postgresql %}
SELECT BuildFrequencyBands();
{% endifdb %}




--CALL BuildNodes(-90,90, FALSE);

