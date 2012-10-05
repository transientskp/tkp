.. _database_assoc:

++++++++++++++++++
Source Association
++++++++++++++++++

Source association—the process by which individual measurements recorded from
an image corresponding to a given time, frequency and Stokes parameter are
combined to form a lightcurve representing an astronomical source—is
fundamental to the goals of the Transients KSP. However, the process is
complex and may be counterintuitive. A thorough understanding is essential
both to enable end-users to interpret pipeline results and to inform pipeline
design decisions.

Here, we summarise the various possible results of source association,
highlighting potential issues. For a full discussion of the algorithms
involved, the user is referred to the thesis by `Scheers
<http://dare.uva.nl/en/record/367374>`_.

Database Structure
==================

The structure of the database is discussed in detail :ref:`elsewhere
<database_schema>`: here, only a brief overview of the relevant tables is
presented.

Each measurement (that is, a set of coordinates, a shape, and a flux) taken is
inserted into the ``extractedsources`` table. Many such measurements may be
taken from a single image, either due to "blind" source finding (that is,
automatically attempting to locate islands of significant bright pixels), or
by a user-requested fit to a specific position.

The association procedure knits together ("associates") the measurements in
``extractedsources`` which are believed to originate from a single
astronomical source. Each such source is given an entry in the
``runningcatalog`` table which ties together all of the measurements. Thus, an
entry in ``runningcatalog`` can be thought of as a reference to the lightcurve
of a particular source.

Each lightcurve may be composed of measurements in one or more frequency
bands (as defined in the ``frequencyband`` table). Within each band flux
measurements are collated. These include the average flux of the source in
that band, as well as assorted measures of variability. Each row in the
``runningcatalog_flux`` table contains flux statistics of this sort for a
given band of a given flux. Thus, each row in ``runningcatalog`` may be
associated with both multiple rows in ``extractedsources`` and in
``runningcatalog_flux``.

Case Studies
============

Here we will discuss the various outcomes which are possible from the source
association process under different conditions. In the following, individual
timesteps are indicated by the notation :math:`t_i` and individual flux measurements
(that is, at a particular time/band/Stokes) by :math:`f_j`. Lightcurves (entries in
``runningcatalog``) are indicated by :math:`L_k`; the flux measurements which
constitute a particular lightcurve are linked to the :math:`L_k` symbol by means of a
coloured line.

Single Frequency Band
---------------------

We start by considering observations with only a single frequency band.

One-to-One Association
++++++++++++++++++++++

.. graphviz:: assoc/one2one.dot

In this simplest case all the flux measurements are unambiguously associated
in order. A single lightcurve is generated. The calculated average flux of the
lightcurve :math:`L_1` is :math:`\overline{f_{1\cdots{}4}}`.

One-to-Many Association
+++++++++++++++++++++++

.. graphviz:: assoc/one2many.dot

Here, both :math:`f_3` and :math:`f_4` can be associated with :math:`f_2` (a
"one-to-many" association).  Since :math:`f_3` and :math:`f_4` are distinct,
though, they result in *two* entries in the ``runningcatalog`` table, or,
equivalently, two lightcurves: :math:`L_1` with average flux
:math:`\overline{f_{1,2,3,5}}` and :math:`L_2` with average flux
:math:`\overline{f_{1,2,4,6}}`.

Note that :math:`f_1` and :math:`f_2`: are now being counted *twice*. Even if
:math:`f_3` and :math:`f_4` each contribute only half the total flux of
:math:`f_2`, the total brightness reached by summing all the lightcurve fluxes
*increases* when this occurs. Equivalently, increasing the spatial resolution
of the telescope causes the sky to get brighter!

Many-to-One Association
+++++++++++++++++++++++

.. graphviz:: assoc/many2one.dot

This situation is similar to that seen above, but in reverse. Initially, two
lightcurves are seen :math:`L_1` consisting of :math:`f_1` and :math:`f_3` and
:math:`L_2` consisting of :math:`f_2` and :math:`f_4`. However, at timestep
:math:`t_3` a new measurement is made, :math:`f_5`, which is associated with both
:math:`f_3` and :math:`f_4`. This, and the subsequent measurement :math:`f_6`,
are then appended to both lightcurves, resulting in :math:`L_1` having average
flux :math:`\overline{f_{1,3,5,6}}` and :math:`L_2` having average flux
:math:`\overline{f_{2,4,5,6}}`. Again, note that :math:`f_5` and :math:`f_6`
are counted twice.

Many-to-Many Association
++++++++++++++++++++++++

.. graphviz:: assoc/many2many.dot

Above, we see first a many-to-many association of :math:`f_3` and :math:`f_4`
with :math:`f_5` and :math:`f_6`. At this point, four separate lightcurves can
be made: :math:`f_{1,3,5}`, :math:`f_{1,3,6}`, :math:`f_{2,4,5}` and
:math:`f_{2,4,6}`. At the next timestep, it's likely that the measurements
:math:`f_7` and :math:`f_8` will be similar to :math:`f_5` and :math:`f_6`
(assuming that the same sources are visible, and neither the sky nor the
telescope configuration has changed). Thus, these are associated and the
number of lightcurves doubles again, as show.

.. note::

    I'm assuming (hoping...) I've got this wrong, because otherwise the number
    of lightcurves increases quadratically whenever there are two sources near
    each other in an image, which is obviously unsustainable.

Multiple Frequency Bands
------------------------

We now introduce the added complexity of multiple bands: the same part of the
sky being observed at the same time, but at different frequencies. Here, we
use just two bands for illustration, but in practice several could be
involved.

Intra-Band One-to-One Association
+++++++++++++++++++++++++++++++++

.. graphviz:: assoc/one2one.multiband.dot

In the simplest case, each measurement undergoes a pair of one-to-one
associations: one with the next measurement of the same source in the same
band, and one with the simultaneous meaurement taken in a different band. A
single entry in the ``runningcatalog`` table result, which we label
:math:`L_1`, but for which two average fluxes are calculated:
:math:`\overline{f_{1\cdots{}4}}` in band 1 and
:math:`\overline{f_{5\cdots{}8}}` in band 2.

Intra-Band One-to-Many Association
++++++++++++++++++++++++++++++++++

.. graphviz:: assoc/one2many.multiband.dot

Here, a one-to-many association takes place in band 1. This results in two
lightcurves: :math:`L_1` with average fluxes :math:`\overline{f_{1,2,3,5}}` in
band 1 and :math:`\overline{f_{7\cdots{}10}}` in band 2, and :math:`L_2` with
average fluxes :math:`\overline{f_{1,2,4,6}}` in band 1 and
:math:`\overline{f_{7\cdots{}10}}` in band 2. Note that the entire flux in
band 2, as well as :math:`f_1` and :math:`f_2`, is now counted twice.

Intra-Band Many-to-One Association
++++++++++++++++++++++++++++++++++

.. graphviz:: assoc/many2one.multiband.dot

Here, a many-to-one association takes place in band 1. This This results in
two lightcurves: :math:`L_1` with average fluxes
:math:`\overline{f_{1,3,5,6}}` in band 1 and
:math:`\overline{f_{7,9,11,13}}` in band 2, and :math:`L_2` with average
fluxes :math:`\overline{f_{2,4,5,6}}` in band 1 and
:math:`\overline{f_{8,10,12,14}}` in band 2.

Inter-Band One-to-Many Association
++++++++++++++++++++++++++++++++++

.. graphviz:: assoc/one2many.crossband.dot

In band 1, a chain of simple one-to-one associations is made. At first,
cross-band one-to-one associations are made between band 1 and band 2.
However, at time :math:`t_3`, :math:`f_3` in band 1 can be associated with
both :math:`f_7` and :math:`f_8` in band 2. However, only :math:`f_7` is
associated with :math:`f_6`, the previous measurement in band 2. Two
lightcurves are generated: :math:`L_1` containing :math:`f_{1\cdots{}4}` in
band 1 and :math:`f_{5,6,7,9}` in band 2, and :math:`L_2`, also containing
:math:`f_{1\cdots{}4}` in band 1 but :math:`f_8` and :math:`f_{10}` in band 2.

Note that the transients pipeline may then backtrack and perform a force-fit
in archival images in an attempt to complete the truncated lightcurve
:math:`L_2` in band 2. This could result in the measurements :math:`f_{11}` and
:math:`f_{12}`. It should be emphasized that this procedure is a
post-processing step, rather than intrinsic to the database, and, as per the
notes below *may be dangerous*.

.. note::

    What happens if :math:`f_{11}` and :math:`f_{12}` can be associated with
    :math:`f_5` and :math:`f_6`? Do the fluxes included in :math:`L_1` change?

.. note::

    Are the positions of the forced fits at :math:`f_{11}` and :math:`f_{12}`
    are based on the position of :math:`f_8` or on the average position of
    :math:`L_2`? In either case, what if they can't be associated with
    :math:`f_1` and :math:`f_2`?

Inter-Band Many-to-One Association
++++++++++++++++++++++++++++++++++

.. graphviz:: assoc/many2one.crossband.dot

In this case, we initially have two well-defined lightcurves. However, at
:math:`t_3`, both lightcurves in band 1 (represented by points :math:`f_5` and
:math:`f_6`) are associated with a single point in band 2 (point
:math:`f_{13}`).

In the event that both :math:`f_{11}` and :math:`f_{12}` are also associated
with :math:`f_{13}`, this reduces to the same situation as the intra-band
many-to-one association discussion above. However, this is not guaranteed: as
in the diagram above, it is possible for :math:`f_{12}` to be associated to a
different point (:math:`f_{15}` in this case). At this point... what???
