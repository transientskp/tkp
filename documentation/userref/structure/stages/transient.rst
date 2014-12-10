.. _stage-transient:

==========================================
Variability and new-source detection stage
==========================================
(See also the
:ref:`relevant configuration parameters<job_params_transient_search>`.)

Variability index calculation
-----------------------------

After all images for a given timestep have been processed and the resulting
source measurements have been assigned to :ref:`runningcatalog
<schema-runningcatalog>` entries (effectively lightcurves), variability
indices are calculated for the most recent timestep, and stored as part of the
association recorded in the :ref:`schema-assocxtrsource` table.

Note that a single runningcatalog source may
contain entries from multiple independent frequency bands. The
variability indices are calculated independently for each frequency band,
hence the :math:`\nu` suffix in the calculations below denotes an index over
the different bands.

For a comprehensive discussion of the transient and variability detection
algorithms currently being employed, see :ref:`Scheers (2011) <scheers-2011>`
chapter 3. Here, we provide a brief outline.

We define two metrics for identifying variability in a lightcurve.
The flux `coefficient of variation <coeff-of-var_>`_, which we
denote :math:`V_\nu`, is defined as

.. math::

   V_{\nu} \equiv \frac{s_{\nu}}{\overline{I_{\nu}}}
           = \frac{1}{\overline{I_{\nu}}} \sqrt{\frac{N}{N-1}(\overline{I^{2}_\nu} - \overline{I_{\nu}}^2)}

where :math:`\overline{I_{\nu}}` is the mean flux of all measurements in the
lightcurve at frequency :math:`\nu`, :math:`s_{\nu}` is the standard deviation
of those flux measurements and :math:`N` is the number of measurements.

The second metric is :math:`\eta_{\nu}`, which is defined based on reduced
:math:`\chi^2` statistics as

.. math::

   \eta_{\nu} \equiv \chi^{2}_{N-1}
              = \frac{1}{N-1} \sum_{i=1}^{N} \frac{(I_{\nu,i} - \overline{I_{\nu}}^*)^2}{\sigma_{I_{\nu,i}}^2}

Where :math:`\overline{I_{\nu}}^*` is the average of the flux measurements
weighed by their uncertainties. :math:`\eta_{\nu}` is the :math:`\chi^{2}`
probability distribution. The probability that the source is "flat" (i.e. has
no significant variability) is then the integral of the distribution from the
measured value of :math:`\eta_{\nu}` to :math:`\infty`; the probability that
it *isn't* flat is thus 1 minus this quantity.

See also the :ref:`appendices on the database schema <schema-appendices>`
for details of how these are iteratively updated.


'New source' detection
----------------------

We also attempt to identify any newly extracted sources which we suspect
are intrinsically variable in nature (i.e. they are getting brighter, as
opposed to our observations getting deeper or even simply looking at a
previously unobserved patch of sky). The algorithm for evaluating new
sources is encoded by
:func:`tkp.db.associations._determine_newsource_previous_limits`.
Sources we deem to be intrinsically 'new' are then recorded in the
:ref:`schema-newsource` table.

.. _coeff-of-var: http://en.wikipedia.org/wiki/Coefficient_of_variation