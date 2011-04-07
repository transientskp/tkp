from __future__ import with_statement
from __future__ import division

"""

Read a parameter set, and return values in dictionary format

(For the moment, this is a quick'n'dirty implementation.
Use lofar.parameterset for more advanced usage.
Though hopefully this module is more Python-esque than the
C++ wrapper variant.)


To do:

  - Support ranges  ( [ value1..value20 ] )

  - Support overriding values when using references. Eg:
    key1.item1 = 10
    key1.item2 = 20
    key2.items = key1
    key2.items.item = 30  # overridden value

  - Support subkeys and values within same key. Eg:
    key1 = value
    key1.item1 = subkey
    
  - Design decision needed:
    Should ParSet contain a recursive dict, or
    be a recursive ParSet itself (since it inherits
    from dict)?


List of changes:

  2010-08-10: Support datetime values
  
  2010-08-09: Support multiline parameters

              Support lists

              Support references
              
  
"""

__author__ = 'Evert Rol / TKP software group'
__email__ = 'evert.astro@gmail.com'
__contact__ = __author__ + ', ' + __email__
__copyright__ = '2010, University of Amsterdam'
__last_modification__ = '2010-08-11'
__version__ = '0.2'


import sys, os
import re
from copy import deepcopy
from datetime import datetime


class ParSetException(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

    
class ParSet(dict):

    def __init__(self, filename_or_fileobj=None):
        if filename_or_fileobj is None:
            d = {}
        elif isinstance(filename_or_fileobj, basestring):
            with open(filename_or_fileobj, "r") as infile:
                d = self._readfile(infile)
        else:
            d = self._readfile(filename_or_fileobj)
        super(ParSet, self).__init__(**d)

    # To do: find a convenient way to keep text inside strings together
    # (eg, comment characters or equal signs)
    def _readfile(self, infile):
        d = {}
        lline = ''
        try:
            for lineno, line in enumerate(infile):
                lline += line.rstrip('\n')
                try:
                    # combine with next line if appended with a backslash
                    if lline[-1] == '\\' and lline[-2] != '\\':
                        # unescaped backslash
                        lline = lline[:-1]
                        continue
                except IndexError:
                    pass
                lline = lline.strip()
                if not lline or lline[0] in '!#%':
                    lline = ''
                    continue
                lline = split_outside_string(r'(?<!\\)#', lline)[0]
                #lline = re.split(r'(?<!\\)#', lline, maxsplit=1)[0]
                lline = lline.strip()
                try:
                    keys, value = self.parse_line(lline)
                    self.setkeys(d, keys, value)
                    #d[key] = value
                except ParSetException:
                    sys.stderr.write("line skipped\n")
                lline = ''
            d = self.parse_refs(d)
            return d
        except (IndexError, ValueError, AttributeError):
            sys.stderr.write("an error occurred on line %d: %s\n" % (
                lineno+1, line.rstrip('\n')))
            raise
                             
    def parse_line(self, line):
        if not "=" in line:
            raise ParSetException("not a valid 'keyword = value' line")
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            raise ParSetException("empty key ine '%s'" % line)
        if not value:
            raise ParSetException("empty key ine '%s'" % line)
        keys = key.split('.')
        value = self.parse_value(value)
        return keys, value

    def parse_value(self, value):
        value = value.strip()
        if value[0] == '[' and value[-1] == ']':
            value = map(self.parse_value,
                        split_outside_string(',', value[1:-1]))
        elif re.search(r'^\d{4}\-\d{1,2}\-\d{1,2}T\d{1,2}:\d{1,2}:\d{1,2}$',
                       value):
            value = datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
        elif value.lower() in ('false', 'no', 'off'):
            value = False
        elif value.lower() in ('true', 'yes', 'on'):
            value = True
        else:
            try:
                value = int(value)
            except ValueError:
                try:
                    value = float(value)
                except ValueError:
                    pass
        return value
        
    def setkeys(self, d, keys, value):
        for key in keys[:-1]:
            d = d.setdefault(key, {})
        d[keys[-1]] = value

    def parse_refs(self, d, orig=None):
        """Parse references to other parameters, and replace"""

        if orig is None:
            orig = deepcopy(d)
        for key, value in deepcopy(d.items()):
            if isinstance(value, dict):
                value.update(self.parse_refs(value, orig))
            elif isinstance(value, basestring):
                value = deepcopy(orig.get(value, value))
            elif isinstance(value, list):
                # This should be solveable through recursion,
                # but I haven't yet figured out how :-(
                for i in range(len(value)):
                    if isinstance(value[i], basestring):
                        value[i] = deepcopy(orig.get(value[i], value[i]))
                        if isinstance(value[i], dict):
                            value[i].update(self.parse_refs(value[i], orig))
                    if isinstance(value[i], basestring):
                        if value[i][0] in ['"', "'"] and value[i][-1] in ['"', "'"]:
                            value[i] = value[i][1:-1]
            if isinstance(value, basestring):
                if value[0] in ['"', "'"] and value[-1] in ['"', "'"]:
                    value = value[1:-1]
            d[key] = value
        return d
            

# Couldn't (yet) find a single regex that does this
def split_outside_string(pattern, string, maxsplit=0):
    """Split a string on pattern, keeping text within quotes
    together

    Pattern can only match single characters
    Escaped characters can't match or function as quotes

    Quotes around text are kept in the result

    Returned is a list of strings
    
    """
    
    strings = []
    in_string = False
    newstring = []
    prevchar = None
    for c in string:
        if c == '\\':
            pass
        elif c in ["'", '"'] and prevchar != '\\':
            # match or set opening quote
            in_string = False if (c == in_string) else c
            newstring.append(c)
        elif in_string:
            newstring.append(c)
        elif re.match(pattern, c) and prevchar != '\\':
            strings.append(''.join(newstring))
            newstring = []
        else:
            newstring.append(c)
        prevchar = c
    if newstring:
        strings.append(''.join(newstring))
    if in_string:
        raise ParSetException("uncorrectly quoted string: %s" % string)
    if maxsplit > 0:
        return strings[0:maxsplit], ''.join(strings[maxsplit:])
    return strings

