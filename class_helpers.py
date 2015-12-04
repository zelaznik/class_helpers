""" A suite of metaprogramming functions which allow more flexible
    class maniuplation such as mixins and monkey patching, while
    still writing "Pythonic" code.

    Works for standard classes (instances of 'type')
    and abstract base classes (instances of abc.ABCMeta)
"""

from abc import ABCMeta
class class_helper_meta(ABCMeta):
    @staticmethod
    def making_surrogate(*args, **kw):
        try:
            name, bases, dct = args
        except ValueError:
            return True
        if kw:
            return True        
        if not isinstance(name, str):
            return True
        if not isinstance(bases, tuple):
            return True
        if not isinstance(dct, dict):
            return True

    def __new__(mcls, *varargs, **kw):
        if mcls.making_surrogate(*varargs, **kw):
            return mcls._wrap(*varargs, **kw)
    
        name, surrogates_or_bases, dct = varargs
        params = {'name': name, 'dct': dct}
        surrogates = []
        bases = []
        for item in surrogates_or_bases:
            if isinstance(item, class_helper_meta):
                surrogates.append(item)
            else:
                bases.append(item)

        bases = params['bases'] = tuple(bases)
        surrogates = params['surrogates'] = tuple(surrogates)

        # Go backward in the event of multiple mixins
        # That was the FIRST mixin is what is most recently
        # Upated to the attributes dictionary
        for surrogate in reversed(surrogates):
            surrogate._unwrap(params)

        if 'cls' in params:
            return params['cls']

        meta = params.get('__metaclass__') or type
        bases = params.get('bases') or ()
        return meta(name, bases, dct)

    @classmethod
    def _wrap(mcls, *args, **dct):
        name = '%s_surrogate' % mcls.__name__
        if len(args) != 1:
            err_msg = "%s() takes exactly 1 argument (%d given)"
            err_args = (mcls.__name__, len(args))
            raise TypeError(err_msg % err_args)

        # Args is either a single value, or an array of values
        try:
            dct['args'] = tuple(args[0])
        except TypeError:
            dct['args'] = (args[0],)
        surrogate = type.__new__(mcls, name, (), dct)
        return surrogate

class include(class_helper_meta):
    """ Copies the attributes from a source
        This allows composition rather than inheritance        
        class Person(Sized, Iterable, Container, include(XYZ)):
            pass
    """
    def _unwrap(self, params):
        dct = params['dct']
        for module in reversed(self.args):
            for base in module.__mro__:
                if base is object:
                    continue
                items = base.__dict__.items()
                for key, value in items:
                    dct[key] = value

class patches(class_helper_meta):
    """ Allows for inline monkeypatching of pure Python classes:
        from collections import namedtuple
        Point = namedtuple(Point,('x','y'))
        class Point(patches(Point)):
            def __abs__(self):
                return sqrt(self.x**2+self.y**2)
    """

    def _unwrap(self, params):
        name, dct = params['name'], params['dct']
        (cls,) = self.args
        if cls.__name__ != name:
            msg = """Inconsistent naming orig=%s, new=%s"""
            raise TypeError(msg % (cls.__name__, name))
        if params['bases']:
            raise TypeError("Cannot alter inheritance of pre-existing class.")
        for key, value in dct.items():
            setattr(cls, key, value)
        params['cls'] = cls
        
class metaclass(class_helper_meta):
    """ Allows for consistent syntax for Python2 and 3
        class Py2_Syntax(A, B):
            __metaclass__ = ABCMeta
        class Py3_Syntax(A, B, metaclass=ABCMeta):
            pass
        class WorksForBoth(A, B, metaclass(ABCMeta)):
            pass
    """
    def _unwrap(self, params):
        (mcls,) = self.args
        params['__metaclass__'] = mcls
        
class inherits(class_helper_meta):
    """ Use this wrapper if you are using a metaclass
        other than the standard "type" and "abc.ABCMeta"

        class ResolvesConflicts(inherits([A,B]), metaclass(SomeMeta)):
            pass
    """
    def _unwrap(self, params):
        if params['bases']:
            msg = "Inconsistent base class layouts."
            raise TypeError(msg)
        params['bases'] = self.args