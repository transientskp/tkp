.. _stage-transient:

===================
Transient detection
===================

After all images for a given timestep have been processed and the resulting
source measurements have been assigned to :ref:`runningcatalog
<schema-runningcatalog>` entries (effectively lightcurves), the resulting data
is searched for transients. Note that a single runningcatalog source may
contain entries from multiple independent frequency band, but currently these
are treated independently for the purposes of transient identification.

For a comprehensive discussion of the transient and variability detection
algorithms currently being employed, see :ref:`Scheers (2011) <scheers-2011>`
chapter 3. Here, we provide a brief outline.

We define two metrics for identifying variability in a lightcurve. The first,
:math:`V_\nu`, is defined as

.. math::

   V_{\nu} \equiv \frac{s_{\nu}}{\overline{I_{\nu}}}
           = \frac{1}{\overline{I_{\nu}}} \sqrt{\frac{N}{N-1}(\overline{I^{2}_\nu} - \overline{I_{\nu}}^2)}

where :math:`\overline{I_{\nu}}` is the mean flux of all measurements in the
lightcurve at frequency :math:`\nu`, :math:`s_{\nu}` is the standard deviation
of those flux measurements and :math:`N` is the number of measurements.
:math:`V_\nu` is the ratio of the variability of the source to its absolute
flux.

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

Source are then identified as transients if they meet *all* of these criteria:

* :math:`V_{\nu}` is above a user-specified threshold;
* :math:`\eta_{\nu}` is above a user-specified threshold;
* The probability of the source not being flat is above a user-specified
  threshold;
* The number of source measurements in the lightcurve is above a
  user-specified threshold.

Once a source has been identified, it is stored in the :ref:`schema-transient`
table in the database.

The following parameters may be configured in the :ref:`job configuration file
<job_params_cfg>`:

Section ``transient_search``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``V_lim``
   Float. :math:`V_{\nu}` must be greater than ``V_lim`` for a source
   to be identified as transient.

``eta_lim``
   Float. :math:`\eta_{\nu}` must be greater than ``eta_lim`` for a source
   to be identified as transient.

``threshold``
   Float. The probability of a source not being flat must be above this threshold for
   it to be identified as transient.

``minpoints``
   Integer. The lightcurve must contain at least ``minpoints`` measurements
   for it to be identified as transient.
