.. _stage-association:

========================
Source association stage
========================
(See also the :ref:`relevant configuration parameters<job_params_association>`.)

After all :ref:`blind <stage-extraction>`
source measurements have been inserted into the database, they are
"associated" with existing sources to form lightcurves. A word on the database
nomenclature may be helpful: we store source measurements (the result of a fit
to a particular collection of image pixels) in a table called
:ref:`extractedsource <schema-extractedsource>`, and multiple extracted
sources are collected together to form a lightcurve by means of the
:ref:`runningcatalog <schema-runningcatalog>` table (see the :ref:`database
schema <database-schema>` documentation for details). This terminology "leaks"
into TraP interfaces, and one will often see references to (for example) a
"runningcatalog source".

The extracted sources are therefore associated with runningcatalog sources.
The association procedure is complex, taking account of multitudinous different
ways in which sources may be related. The detailed documentation on
:ref:`database-assoc` covers all the possible association topologies and
describes the code pathways in detail; see also :ref:`Scheers (2011)
<scheers-2011>`.



