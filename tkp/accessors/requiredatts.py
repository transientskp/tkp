from abc import ABCMeta

class RequiredAttributesMetaclass(ABCMeta):
    """
    Provides instantiation-time checking for 'required attributes'.

    This can be used to define an 'interface' of sorts. Use it to define
    an abstract base class that specifies all the attributes you expect
    to see from user-defined classes in a given situation.

    Usage:
    Set this as the metaclass for an abstract base class which defines an
    iterable, ``_required_attributes``, as a class-attribute,
    e.g. (in Python 2 syntax)::

        class BasicRequirements(object):
            __metaclass__ = RequiredAttributesMetaclass
            _required_attributes = [
                'foo',
                'bar',
            ]

    Then, any inheriting classes will only instantiate if all the required
    attributes are both defined and not None.
    Defining the inheriting class works as normal, e.g.::

        class SomeBasicClass(BasicRequirements):
            def __init__(self):
                self.foo = 123
                self.bar = 456

    The metaclass supports use of 'mixin' abstract
    classes that specify additional (possibly overlapping)
    requirement sets, so e.g. we could have create an extra
    set of requirements::

        class ExtraRequirements(object):
            __metaclass__ = RequiredAttributesMetaclass
            _required_attributes = [
                'bar',
                'baz',
            ]

    and use it to provide instantiation-time checking for
    a class that requires all of the above::

        class SomeSpecialClass(BasicRequirements,ExtraRequirements):
            def __init__(self):
                self.foo = 12
                self.bar = 34
                self.baz = 56


    Finally, note that we inherit from metaclass ABCMeta,
    so any use of e.g. @abstractmethod, @abstractproperty
    decorators will work the same as with a regular
    ABCMeta abstract base class.

    """
    def __call__(cls, *args, **kwargs):
        obj = type.__call__(cls, *args, **kwargs)
        required_atts=set()
        for cls in obj.__class__.__mro__:
            if hasattr(cls,'_required_attributes'):
                required_atts = required_atts.union(cls._required_attributes)
        for attr in required_atts:
            if not hasattr(obj,attr) or (getattr(obj,attr) is None):
                raise NotImplementedError(
                    "Uninitialized attribute: {}\n"
                    "(Class '{}' must initialize attributes {})".format(
                        attr,
                        obj.__class__.__name__,
                        required_atts)
                )
        return obj