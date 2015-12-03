""" A suite of metaprogramming functions which allow more flexible
    class maniuplation such as mixins and monkey patching, while
    still writing "Pythonic" code.
"""

class class_helper_meta(type):
    def __new__(mcls, *args):
        if len(args) == 1:
            return mcls.__wrap(*args)
        elif len(args) == 3:
            return mcls.__unwrap(*args)

    @classmethod
    def __wrap(mcls, item):
        bases = (item,)
        name = 'patches_%s' % item.__name__
        args = (mcls, name, bases, {})
        surrogate = type.__new__(*args)
        return surrogate

class patches(class_helper_meta):
    """ Allows for inline editing of Python classes.  Especially useful
        when fiddling with code in an interactive Python session.
        
        EXAMPLE:
            from collections import namedtuple
            Person = namedtuple('Person',('first_name','last_name'))
            orig_class = Person
            class Person(patches(Person)):
                @property
                def full_name(self):
                    return ' '.join([self.first_name, self.last_name])
            assert Person is orig_class

        I built this specifically to be able to use collections.namedtuple.
        This way I can use the their template but still add my own features,
        without adding an unncessary subclass, or doing ugly monkeypatching.
    """

    @classmethod
    def __unwrap(mcls, name, bases, dct):
        if len(bases) != 1 or not isinstance(bases[0], patches):
            d = {'name':name,'bases':bases,'dct':dct}
            raise ValueError("Invalid arguments: %r" % d)

        (surrogate,) = bases
        (cls,) = surrogate.__bases__

        if cls.__name__ != name:
            msg = """Inconsistent naming orig=%s, new=%s"""
            raise ValueError(msg % (cls.__name__, name))

        for name, value in dct.items():
            setattr(cls, name, value)

        return cls
        










        