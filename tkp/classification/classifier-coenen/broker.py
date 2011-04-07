# By Thijs Coenen february 2007 for Masters Thesis Research with the 
# Transients Key Project of LOFAR.

# Work in progress! Indentation done using 4 spaces instead of tabs.

# to do:
# -clean up the meta data / selection stuff (find useful abstraction)
# -error checking everywhere
# -implement proper storage backends (not the placeholders currently in place)
# -be a bit smarter with keyboard input (currently that is in prompt_user object)

"""This module holds the broker object and everything it absolutely needs to 
function. Everything is assumed to be labeled with time, integration time, 
frequency, bandwidth and unique id.

iteration 4, version 2007-02-20"""


from types import *

# -----------------------------------------------------------
# ----- metadata object used to label everything in system --

class metadata(object):
    """Metadata object is attached to each object in the broker system.
    For now it is assumed that all data is labeled with:
    -time: t
    -integration time: dt
    -frequency: nu
    -bandwidth: dnu
    -a unique id: ID"""
    __slots__ = ['t', 'dt', 'nu', 'dnu', 'ID']
    def __init__(self, t = 0, dt = 0, nu = 0, dnu = 0, ID = 0):
        self.t = t
        self.dt = dt
        self.nu = nu
        self.dnu = dnu
        self.ID = ID

def overlap(x1, dx1, x2, dx2):
    if x1 == None or x2 == None or dx1 == None or dx2 == None:
        return True # since selecting based on this criterion is useless
    if x1 + dx1 < x2 or x1 > x2 + dx2:
        return False # overlap
    return True # no overlap

def select(t, dt, nu, dnu, ID, metadata):
    # not good looking, but works, will rewrite to more concise (XXX FIXME)
    overlap_t = overlap(t, dt, metadata.t, metadata.dt)
    overlap_nu = overlap(nu, dnu, metadata.nu, metadata.dnu)
    if ID != None and metadata.ID != None:
        if ID == metadata.ID:
            match = True
        else:
            match = False
    else:
        match = True
    return overlap_t and overlap_nu and match

# -------------------------------------------------
# ------- stand-ins for storage backends ----------

class naive_memory_store(object):
    """Place holder for more involved storage methods.
    Create an instance of this object and register
    the store and retrieve functions with the broker
    object."""
    def __init__(self):
        self.container = []
    def store(self, objects):
        assert type(objects) == ListType
        self.container.extend(objects)
    def retrieve(self, some_class, t, dt, nu, dnu, ID):
        assert type(some_class) == TypeType
        return [x for x in self.container if select(t, dt, nu, dnu, ID, x.metadata) and some_class == x.__class__]
    def dump(self):
        print self.container

class naive_pysqlite_store(object): # work in progress / not functional yet
    def __init__(self):
        from pysqlite2 import dbapi2 as sqlite
        self.sqlite = sqlite
        self.connection = self.sqlite.connect(":memory:")
        self.cursor = self.connection.cursor()

# --------------------------------------------------
# ------- the broker (brains of the operation) -----

class broker(object):
    """The broker object keeps track of how to store or retrieve
    instances of the classes that are derived from TKP data."""
    def __init__(self):
        self.store_functions = {}
        self.retrieve_functions = {}
        self.create_functions = {}
        self.dependencies = {}
        
    def register_store(self, some_class, function):
        """This function associates a certain class of objects to
        a certain function that does the storing."""
        assert type(some_class) == TypeType
        assert type(function) in [FunctionType, MethodType]
        self.store_functions[some_class] = function
        
    def register_retrieve(self, some_class, function):
        """This function associates a certain class of objects to
        a certain function that does the retrieving of those objects."""
        assert type(some_class) == TypeType
        assert type(function) in [FunctionType, MethodType]
        self.retrieve_functions[some_class] = function
        
    def register_create(self, some_class, function, dependencies):
        """This function registers the way a certain class of objects
        depends on others and which function can be used to create
        these objects (based on the input of the others).
        
        If need be there can be several ways of creating the objects.
        Raw data or level zero data should of course not be registered
        with this function ;)"""
        assert type(some_class) == TypeType, some_class
        assert type(function) in [FunctionType, MethodType]
        for x in dependencies:
            assert type(x) == TypeType
        if self.create_functions.has_key(some_class):
            self.create_functions[some_class].append(function)
            self.dependencies[some_class].append(dependencies)
        else:
            self.create_functions[some_class] = [function]
            self.dependencies[some_class] = [dependencies]
        
    def store(self, objects):
        """Used to store an object of a certain class (this maps the
        input list of objects to the relevant storage function)."""
        assert type(objects) == ListType
        for X in objects:
            try:
                self.store_functions[X.__class__]([X]) # ahem! fugly
            except:
                if not self.store_functions.has_key(X.__class__):
                    print "storage function not registered -> retrieval failed"
                else:
                    print "storage function registered -> retrieval failed"
                
    def retrieve(self, some_class, t, dt, nu, dnu, ID = None):
        """Used to retrieve objects of a certain class at a certain
        region in t and/or nu space and/or with a certain ID.
        
        If nothing is available in storage no derivation is attempted."""
        assert type(some_class) == TypeType
        try:
            result = self.retrieve_functions[some_class](some_class, t, dt, nu, dnu, ID)
        except:
            result = []
            if not self.retrieve_functions.has_key(some_class):
                print "retrieval function not registered -> retrieval failed"
            else:
                print "retrieval function registered -> retrieval failed"
        return result
        
    def query(self, some_class, t, dt, nu, dnu, ID, recurs = 5):
        """Used to retrieve objects of a certain class at a certain
        region in t and/or nu space and/or with a certain ID.
        
        If nothing is available in storage a derivation is attempted.
        This function recursively looks for objects that might be 
        needed in the derivation."""
        assert type(some_class) == TypeType
        if recurs == 0:
            return []
        result = self.retrieve(some_class, t, dt, nu, dnu, ID)
        if result == [] and some_class in self.create_functions:
            for i in range(len(self.create_functions[some_class])):
                dependencies_found = True
                dependencies = {}
                for dep in self.dependencies[some_class][i]:
                    assert type(dep) == TypeType
                    tmp = self.query(dep, t, dt, nu, dnu, recurs - 1)
                    if tmp == []:
                        dependencies_found = False
                        break
                    else:
                        dependencies[dep] = tmp
                if dependencies_found == True:
                    result = self.create_functions[some_class][i](dependencies)
                    if result != []:
                        break
        else:
            if __debug__:
                print "retrieved", result
            return result
        if result != []:
            if __debug__:
                print "created", result
            self.store(result)
            return result
        else:
            print "failure", result
            return result

if __name__ == "__main__":
    print "useless self test :P"