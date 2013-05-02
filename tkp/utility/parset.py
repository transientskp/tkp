
class Parset(dict):
    """
    a pure Python parameterset parser
    """

    def __init__(self, filename=None):
        """
        Create a parameterset object.
        """
        self.filename = filename
        self._parse_file(self.filename)

    def _parse_file(self, filename):
        self._data = {}
        for line in open(filename):
            if '#' in line:
                line = line.split('#')[0]
            if '=' in line:
                key, value = line.split('=', 1)
                self[key.strip()] = value.strip()

    def makeSubset(self, baseKey, prefix=''):
        """Return a subset as a new parameterset object.

        baseKey
          The leading part of the parameter name denoting the subset.
          A trailing period needs to be given.
        prefix
          The baseKey parameter name part is replaced by this new prefix.
          The default new prefix is empty.

        For example::

          newps = ps.makeSubset ('p1.p2.', 'pr.')

        creates a subset of all keys starting with `p1.p2.` and replaces
        that prefix by `pr.`.

        """
        raise NotImplementedError

    def getVector(self, key):
        """Get the value as a vector of values."""
        return [self[key]]

    def getRecord(self, key):
        """Get the value as a record."""
        return self[key]

    def dict(self):
        """Turn the parset into a dict"""
        return self

    def getBoolVector(self, key, default=None, expandable=False):
        """Get the value as a list of boolean values.

        key
          Parameter name
        default
          Default value to be used if parameter is undefined.
          If None is given, an exception is raised if undefined.
        expandable
          True = ranges and repeats (.. and *) are expanded first.

        """
        if expandable:
            raise NotImplementedError
        return [bool(self.get(key, default))]

    def getIntVector(self, key, default=None, expandable=False):
        """Get the value as a list of integer values.

        key
          Parameter name
        default
          Default value to be used if parameter is undefined.
          If None is given, an exception is raised if undefined.
        expandable
          True = ranges and repeats (.. and *) are expanded first.

        """
        if expandable:
            raise NotImplementedError
        return [int(self.get(key, default))]

    def getFloatVector(self, key, default=None, expandable=False):
        """Get the value as a list of floating point values.

        key
          Parameter name
        default
          Default value to be used if parameter is undefined.
          If None is given, an exception is raised if undefined.
        expandable
          True = ranges and repeats (.. and *) are expanded first.

        """
        if expandable:
            raise NotImplementedError
        return [float(self.get(key, default))]

    def getDoubleVector(self, key, default=None, expandable=False):
        """Get the value as a list of floating point values.

        key
          Parameter name
        default
          Default value to be used if parameter is undefined.
          If None is given, an exception is raised if undefined.
        expandable
          True = ranges and repeats (.. and *) are expanded first.

        """
        if expandable:
            raise NotImplementedError
        return [float(self.get(key, default))]

    def getStringVector(self, key, default=None, expandable=False):
        """Get the value as a list of string values.

        key
          Parameter name
        default
          Default value to be used if parameter is undefined.
          If None is given, an exception is raised if undefined.
        expandable
          True = ranges and repeats (.. and *) are expanded first.

        """
        if expandable:
            raise NotImplementedError
        return [str(self.get(key, default))]

    def add(self, PyParameterSet, *args, **kwargs):
        raise NotImplementedError

    def adoptCollection(self):
        raise NotImplementedError

    def adoptFile(self):
        raise NotImplementedError

    def fullModuleName(self):
        raise NotImplementedError

    def getBool(self, key, default=None):
        return bool(self.get(key, default))

    def getDouble(self, key, default=None):
        return float(self.get(key, default))

    def getFloat(self, key, default=None):
        return float(self.get(key, default))

    def getInt(self, key, default=None):
        return int(self.get(key, default))

    def getString(self, key, default=None):
        return str(self.get(key, default))

    def isDefined(self, key):
        return key in self._data

    def keywords(self):
        return self.keys()

    def remove(self, key):
        self.pop(key)

    def replace(self, key, value):
        self[key] = value

    def size(self):
        return len(self._data)

    def locateModule(self):
        raise NotImplementedError

    def subtractSubset(self):
        raise NotImplementedError

    def version(self):
        raise NotImplementedError

    def writeFile(self):
        raise NotImplementedError

    def isRecord(self):
        raise NotImplementedError

    def isVector(self):
        raise NotImplementedError

    def __reduce__(self):
        raise NotImplementedError