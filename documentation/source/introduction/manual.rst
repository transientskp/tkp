.. _manual_classification:

+++++++++++++++++++++
Manual classification
+++++++++++++++++++++


**NOTE** this is outdated since 2011: the transients pipeline does not
  an XML scheme anymore for manual classification.

Sources will be manually classified, following user defined
schemes. The purpose of the manual classification system is to account
for exceptional events, or well-known sources that go into outburst
and have a catalogus source associated, thus practically eliminating
the need for automatic classification (assuming that it is not
important what the outburst looks like, just the outburst fact
itself).

This requires clearly defined characteristics, that can be extracted
as features from the light curve, spectrum or source
shape. Associations with catalogued sources in the Glocal Sky Model or
other databases (either one like NVVS or WENS, or small ones
containing, eg, gamma-ray burst positions or X-ray binaries) are also a
possible (and straightforward) characteristic, as are associations
with VO-events (transients at other wavelengths).

The characteristics and conditions that define a particular transient
are described using an XML scheme, that basically walks through a tree
of conditions and testing those using extracted features from the
transient source.

There is as of 08-09-2010 not yet a full-blown XSD schema for the XML
file that stores manual classification tests. Below, however, an
overview is given that should help users to insert their own tests,
and thus allowing them to classify their own transient.

Description of the XML scheme
=============================

The manual classification system relies on tests that are comprised of
simple comparisons, chained together with ``and`` and ``or``
operators. These tests compare various characteristics of the
light curve or spectrum with fixed values, or sometimes just check if
the characteristic is available (eg, a database match). Based on the
outcome, a weight is assigned to the specific classification
characteristic.

Overall structure
-----------------

The overall structure starts at a ``branch``, and uses a test to
determine which part of the branch to follow. Such a test consists of
a condition and several outcomes (most often, ``true``, ``false`` or
``N/A`` for not available). The outcomes each define their own
``action``, that could include a next branch, simply a weight that
gets added to a specific source classification, or a series of tests
that will be run through for source classification. The condition
consists of one or more comparisons, that compare transient
characteristics with predefined values.

For tests that have ``weight`` actions, the weight gets added to the
specific classification that belongs to that test. In this way,
various source classification are tested, each obtaining a certain
weight; at the end of the walk through the XML structure, the Python
code will have created a dictionary of possible classifications (the
dictionary keys) and their weights (the dictionary values).





Walking the XML structure
-------------------------

The XML structure is housed inside the ``<transient-classification-scheme>``
element, and starts with a branch. The branch consists of a test (that
houses a condition), and one or more outcomes, that select the branch
to continue. A simple example is::

    <transient-classification-scheme>
      <branch name="point source" id="branch:point-source">
        <test name="point source">
          <condition>
            <variable>self</variable>
            <compare op="eq">
              <attribute>shape</attribute>
              <value type="string">point</value>
            </compare>
          </condition>
          <outcome>
            <value type="bool">true</value>
            <value type="special">N/A</value>
            <action type="branch">
              <!-- next branch -->
            </action>
          </outcome>
          <outcome>
            <value type="bool">false</value>
            <action type="branch">
              <!-- perform tests to classify extended sources -->
            </action>
          </outcome>
        </test>
      </branch>
    </transient-classification-scheme>

In this case, the transient object (``self``) may have a
characteristic (an ``<attribute>``) ``shape``, that is checked whether it
is "point". If it is, or there is no ``shape`` attribute (``N/A``), the "point"
branch is chosen, otherwise, tests for classifying extended sources
are run.

Branches can be nested, but at some point one needs to classify a
source. This can be done inside a ``<classification>`` element, which
generally is used inside a ``<branch>``. Such a ``<classification>``
consists of one or more tests (as described in the next section)
inside a ``<rule>``. Each test adds a weight to the specific source
classification, with a resulting set of classification--weight pairs.

Extending the second branch in the above example, we could have::

    <outcome>
      <value type="bool">false</value>
      <action type="branch">
        <classification id="classification:fast-extended" name="Fast variable extended source">
          <rule>
            <type>weights</type>
            <test refer="test:fast-extended-source-light-curve-duration" />
          </rule>
        </classification>
      </action>
    </outcome>

which has just one test. The ``name`` attribute in the
``<classification>`` tag sets the key for the Python dictionary that, in
the end, will continue all the possible source classification.

Note the ``refer`` attribute in the ``<test>`` tag: it refers to a
test previously defined (outside the
``<transient-classification-scheme>``, actually).  Adding more tests
is easy (since the outcomes of the tests just add together, as long as
the ``<rule>`` is of ``<type>`` ``weights``)::

    <rule>
      <type>weights</type>
      <test refer="test:fast-extended-source-light-curve-duration" />
      <test refer="test:extended-source-invert-spectrum" />
    </rule>


Of course, this tells you nothing how a test is actually defined, and
what weight is attached to a classification (or more specifically, how
much weight is attached to one particular classified aspect of the
source). That is explained in the next section.

Tests
-----

A simple test can look like the following::

    <test id="test:GRB-prompt-emission-light-curve-variability" name="light curve variability">
      <condition>
        <variable>self</variable>
        <compare op="lt">
          <attribute>variability</attribute>
          <value type="float">1.0e-1</value>
        </compare>
      </condition>
      <outcome>
        <value type="bool">true</value>
        <action type="weight">0.5</action>
      </outcome>
      <outcome>
        <value type="bool">false</value>
        <value type="special">N/A</value>
        <action type="weight">0.0</action>
      </outcome>
    </test>

Thus, the ``variability`` attribute of the transient (the variable
``self``) is compared a float with value 0.1. If the variability is
lower than (``lt``) 0.1, the outcome is ``true`` and a weight of 0.5
is added to the classification (the classification is not defined
here, but see the examples in the previous section). If the
variability is larger than (or equal to) 0.1, or the variability
attribute is simply not available (because there is too little light
curve information to estimate it), the outcome is ``false`` or
``N/A``, and the weight added to this source classification is simply
0.

Finally, the ``id`` attribute is what is referred to when tests are
included inside a ``<classification>`` element; the ``name`` attribute is
just a convenience, and not yet used.

Details
-------

The transient characteristics are actually named 'attributes' inside
the XML scheme, hinting at the Python code that uses the XML scheme to
decide on the transient. An attribute is defined using the
``<attribute>name</attribute>`` tag.

A variable also needs to be given. Most often, this will be ``self``
(very Pythonic), indicating the transient object in question. In some
cases, variables like ``external-trigger`` (a VO-event) or
``database`` might be given, in which case it will look at this
specific variable. The variable is defined using the
``<variable>name</variable>`` tag. *Note: this will likely change in
the near-future, and there will only be one variable, the transient
object. In which case the variable does not need to be given anymore.*

A comparison is created using the ``<compare>`` tag. A compare tag has
a required ``op`` attribute to define the comparisons.  The comparison
operators that can be used are ``eq``, ``neq``, ``lt``, ``gt``,
``lte``, ``gte``, ``and``, ``or`` and ``match``, with their obvious
meanings. Only ``match`` is exceptional: it is used to match a
variable where a precise ``eq`` would not suffice. For example, in the
case of a position (match a position with a well-known source
position), the match has to be within precision. ``match`` therefore
involves an extra ``precision`` attribute for the ``<compare>``
tag. Finally, the ``and`` and ``or`` operators are for chaining
multiple comparisons.

``<compare>`` needs two elements, which can either be comparisons again
(for ``and`` and ``or``), an ``<attribute>`` element, or a ``<value>``
element. The latter is used to compare directly to an actual
value. ``<value>`` has a required attribute ``type``, which can be one of
``float``, ``bool``, ``string``, ``integer`` or ``special``
(currently, only if the value is ``N/A``). There is an optional
``unit`` attribute, but that is currently ignored.



Insert your own classification
------------------------------

With the above, and the example classification.xml file provided in
the tkp.classification.manual module directory, it should be
straightforward to define your own tests, and insert them at
appropriate places in the ``<transient-classification-scheme>``. Most of
them will be copy-paste-adapt from previous tests.

It is likely, however, that at some point you need new attributes of
the transient object, that are not yet available. This would mean
adopting the feature extraction recipe to your own needs, extending it
to include the new characteristics. But always keep a ``<value
type="special">N/A</value>`` element in your tests: never assume that
a feature is always available.

Finally, the current structure is still somewhat rough, occasionally
abundant in XML-tags, while on other occasions a necessary tag may be
lacking. A validator has not been written, nor proper unit tests, but
once the structure settles down, this will happen as well. In the mean
time, keep an eye out for changes.
