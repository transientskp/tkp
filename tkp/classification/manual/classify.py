"""

The classify module contains the main ClassificationSchema class, that
can parse an XML classification schema and return a set of weights for
possible identifications of a transient.

Further classes defined here are:

- the DataBase class, which represents a match with an external
  database

- the ExternalTrigger class, which represents an external trigger,
  such as a VO Event or a LOFAR follow-up trigger.
  The actual trigger probably gets accessed through a database

"""

import sys
from math import sqrt
from .etree import ElementTree
from .transient import Transient
from .utils import Position, DateTime


__version__ = "0.3"
__author__ = "Evert Rol"
__email__ = "evert.astro@googlemail.com"
__copyright__ = "University of Amsterdam, 2010"

__all__ = ("ClassificationSchema",
           "Position",
           "DateTime",
           "Transient",
           "ExternalTrigger",
           "DataBase")

# condition names and corresponding variablenames
CONDITION_VARIABLES = {'self': 'transient',
                       'external-trigger': 'trigger',
                       'database': 'database'}
NAMESPACE = "{http://transientskp.org/classification}"
NSMAP = {"tkp": "http://transientskp.org/classification"}

# Python 2/3 compabitiliy fix
try:
    string = basestring
except NameError:
    string = str


class ExternalTrigger(object):
    """Class that represents an external trigger

    This class represents an external trigger, such as
    
    - VOEvents

    - Internal LOFAR trigger (e.g. for follow-up)
    
    """
    
    def __init__(self, position=None, timezero=None):
        if isinstance(position, Position):
            self.position = position
        else:
            self.position = Position(ra=123.456, dec=12.345)
        if isinstance(timezero, DateTime):
            self.timezero = timezero
        else:
            self.timezero = DateTime(2010, 2, 3, 16, 35, 42, error=0.5)

    def __str__(self):
        return "external trigger at %s" % (str(self.timezero),)

    def __repr__(self):
        return "ExternalTrigger(position=%s, timezero=%s)" % (
            repr(self.position), repr(self.timezero))


class DataBase(object):
    """Class that represents a database, or rather a database object

    An identified transient that has a database association, will have
    that assocation in this class.
    Otherwise, this class is very simple, containing only the name of the
    database, and an assocation flag that in practice will always be True
    
    """
    
    def __init__(self, name="", association=True):
        self.association = association
        self.name = name
        
    def __str__(self):
        return "database %s" % (self.name,)

    def __repr__(self):
        return "DataBase(name=%s, association=%s)" % (
            self.name, self.association)
                                     
    
def varconvert(value, vartype, logger=None):
    """Convert an arbitrary object of 'vartype' into a proper Python object"""

    # avoid eval()
    if vartype in ('special'):
        if value == 'N/A':
            value = None
    elif vartype in ('bool', 'boolean'):
        if isinstance(value, string):
            if value.lower() == 'false':
                value = False
            elif value.lower() == 'true':
                value = True
            else:
                raise ValueError("%s is not a valid boolean type" % value)
        else:
            value = bool(value)
    elif vartype in ('float', 'double'):
        value = float(value)
    elif vartype in ('int', 'integer', 'long'):
        value = int(value)
    elif vartype in ('position',):
        if isinstance(value, (tuple, list)):
            if len(value) == 2:
                value = Position(value[0], value[1])
            elif len(value) == 3:
                value = Position(value[0], value[1], value[2])
    elif vartype in ('datetime',):
        if not isinstance(value, DateTime):
            pass
    elif vartype in ('string',):
        value = str(value)
    return value


def convert_valuenode(node, logger=None):
    """convert a <value /> into a Python object"""
    
    try:
        value = varconvert(node.text, node.attrib['type'], logger=logger)
    except KeyError:
        value = node.text   # use the plain string value
    return value


class ClassificationSchema(object):
    """Represents an XML classification schema

    Use a ClassificationSchema instance to classify a Transient instance.
    The ClassificationSchema instance will read an XML classification
    schema on creation.

    It can then be run multiple times, with different inputs (Transient,
    ExternalTrigger, DataBase).

    The basic usage is::

        >>> schema = ClassificationSchema("classification.xml")
        >>> schema.run(transient1, trigger1, database1)
        >>> schema.run(transient2, trigger2, database2)
        >>> schema.run(transient3, trigger3, database3)
        >>> schema.run(transient4, trigger4, database4)

    Every run results in a set of weights; only those weights that were
    evaluated are returned. That is, if the XML schema branches, then only
    the possible outcomes for that branch are calculated; the outcomes in
    the other branch will be ignored.
    
    The set of weights is returned as a dictionary, with the keys being
    the source description, and the value being the corresponding weight.
    
    """
    
    def __init__(self, filename=None, verbose=False):
        self.filename = filename
        self.verbose = verbose
        # Immediately read the XML file, so it's ready for multiple uses
        self.tree = ElementTree.parse(self.filename)
        self.transient = self.trigger = self.database = None
        self.weights = {}
        
    def run(self, transient=None, trigger=None, database=None, verbose=None, logger=None):
        self.transient = transient
        self.trigger = trigger
        self.database = database
        self.weights = {}
        if verbose is not None:
            self.verbose = verbose
        self.logger = logger
        return self.parse()
    
    def parse(self):
        """Start parsing the XML tree"""
        
        mainnode = self.tree.find(NAMESPACE + "transient-classification-scheme")
        self._branch(mainnode)
        return self.weights
    
    def _branch(self, node):
        """Branch off if there are branches; otherwise run the tests inside
        the branch"""
        
        for branch in node.findall(NAMESPACE + "branch"):
            self._test(branch.find(NAMESPACE + "test"))
        for tree in node.findall(NAMESPACE + "classification"):
            self.weights[tree.get('name')] = self._classify(tree)
        
    def _classify(self, roottree):
        """Classify a single source type

        This will run through several tests, and return a combined weight
        from the test results

        """
        
        totalweight = 0
        for testnode in roottree.find(NAMESPACE + "rule").findall(
            NAMESPACE + "test"):
            if 'refer' in testnode.attrib:
                xpath = NAMESPACE + "test[@id='%s']" % testnode.attrib['refer']
                tnode = self.tree.find(xpath)
            else:
                tnode = testnode
            weight = self._test(tnode)
            totalweight += weight
            if self.verbose:
                sys.stdout.write("- %s: %.2f\n" % (tnode.get('name'), weight))
        return totalweight

    def _test(self, testtree):
        """Run a single test, and return the corresponding outcome (=weight)"""
        
        outcome = 0
        result = self._condition(testtree.find(NAMESPACE + "condition"))
        for node in testtree.findall(NAMESPACE + "outcome"):
            outcome += self._outcome(node, result)
        return outcome

    def _condition(self, tree):
        """Parse a condition, and return the result

        In general, the result of a condition will simply be true or false

        """
        
        cond_type = tree.find(NAMESPACE + "variable").text
        result = []
        for condition, variable in CONDITION_VARIABLES.items():
            if cond_type == condition:
                for comptree in tree.findall(NAMESPACE + "compare"):
                    result.append(self._compare(
                        comptree, variable=self.__getattribute__(variable)))
                if len(result) > 1:
                    result = reduce(lambda x, y: x is True and y is True,
                                    result)
                else:
                    result = result[0]
        return result
            
    def _compare(self, node, variable=None, result=None):
        """Compare an attribute of the transient with a value in the
        classification schema

        This method compares the various attributes of a Transient instance
        with value(s) given in the XML classification schema.
        It can also compare an attribute with one of the 'external' variables
        given in the run() method (ExternalTrigger, DataBase), so that
        matches with a VOEvent or assocations with external databases are
        possible.

        The XML classification schema defines how the comparison is done,
        that is, with what precision, and which operator (equal to,
        lower than, greater than or equal to, etc).

        """
        
        comps = []
        value = attribute = None
        precision = 0
        try:
            operand = node.attrib['op']
        except KeyError:
            raise AttributeError("missing 'op' attribute in: %s" %
                                 eltree2string(node))
        if operand == 'match':
            try:
                precision = float(node.attrib['precision'])
            except KeyError:
                precision = 0
        for childnode in node:
            if childnode.tag == NAMESPACE + "compare":
                comps.append(self._compare(childnode, variable=variable))
            elif childnode.tag == NAMESPACE + "attribute":
                if variable is None:
                    raise ValueError("no variable defined for %s" %
                                     eltree2string(childnode))
                attribute = childnode.text
            elif childnode.tag == NAMESPACE + "value":
                vartype = childnode.attrib['type']
                value = convert_valuenode(childnode, logger=self.logger)
            elif childnode.tag == NAMESPACE + "type":
                vartype = childnode.text
        if attribute is not None:
            try:
                if value is None:
                    # no <value> node found; compare to transient
                    variable = varconvert(variable.__getattribute__(attribute),
                                          vartype)
                    value = varconvert(
                        self.transient.__getattribute__(attribute), vartype)
                    if value is None:
                        return None
                else:
                    tmp = variable.__getattribute__(attribute)
                    if tmp is not None:
                        variable = varconvert(tmp, vartype, logger=self.logger)
                    else:
                        return None
                    
            except AttributeError:
                # Needs checking whether this hides real errors
                return None

        # Perform the actual comparison, according to the operand.
        if len(comps) == 0:
            comps = [variable, value]
        if operand == 'eq':
            result = comps[0] == comps[1]
        elif operand == 'neq':
            result = comps[0] != comps[1]
        elif operand == 'gt':
            result = comps[0] > comps[1]
        elif operand == 'lt':
            result = comps[0] < comps[1]
        elif operand == 'gte':
            result = comps[0] >= comps[1]
        elif operand == 'lte':
            result = comps[0] <= comps[1]
        elif operand == 'and':
            result = comps[0] and comps[1]
        elif operand == 'or':
            result = comps[0] or comps[1]
        elif operand == 'match':
            result = comps[0].match(comps[1], precision=precision)
        return result

    def _outcome(self, node, result=None):
        """Select the correct outcome part of the XML tree

        This method compares the various outcomes from the _test() method
        to the possible outcome values given in the classification, and
        returns the result from positive matches.

        Results can be a weight value, or a new branch. In the latter case,
        the method recursively branches into this new branch.

        """
        
        retval = 0
        for valuenode in node.findall(NAMESPACE + "value"):
            value = convert_valuenode(valuenode)
            if result == value:
                action = node.find(NAMESPACE + "action")
                actiontype = action.attrib['type']
                if actiontype == 'weight':
                    retval = float(action.text)
                elif actiontype == 'branch':
                    self._branch(action)
                    retval = 0
                break
        return retval
