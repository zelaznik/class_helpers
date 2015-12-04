""" A suite of metaprogramming functions which allow more flexible
    class maniuplation such as mixins and monkey patching, while
    still writing "Pythonic" code.
"""

class class_helper_meta(type):
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

    def __new__(mcls, *args, **kw):
        try:
            if mcls.making_surrogate(*args, **kw):
                return mcls._wrap(*args, **kw)
        
            name, surrogates_or_bases, dct = args
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

            for surrogate in surrogates:
                surrogate._unwrap(params)
    
            if 'cls' in params:
                return params['cls']
    
            meta = params.get('__metaclass__') or type
            bases = params.get('bases') or ()
            return meta.__new__(meta, name, bases, dct)
        except Exception:
            globals().update(locals())
            raise

    @classmethod
    def _wrap(mcls, *args, **dct):
        name = '%s_surrogate' % mcls.__name__
        dct['args'] = args
        surrogate = type.__new__(mcls, name, (), dct)
        return surrogate

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
            raise ValueError(msg % (cls.__name__, name))
        for key, value in dct.items():
            setattr(cls, key, value)
        params['cls'] = cls
        
class metaclass(class_helper_meta):
    """ Allows for consistent syntax for Python2 and 3
        class Py2_Syntax(A, B):
            __metaclass__ = ABCMeta
        class Py3_Syntax(A, B, metaclass=ABCMeta):
            pass
        class WorksForBoth(inherits(A,B), metaclass(ABCMeta)):
            pass
    """
    def _unwrap(self, params):
        (mcls,) = self.args
        params['__metaclass__'] = mcls
        
class inherits(class_helper_meta):
    """ To be used with the "metaclass" helper.  See doc below:
        %s """ % metaclass.__doc__
    def _unwrap(self, params):
        params['bases'] = self.args

class mixin(class_helper_meta):
    """ Copies the attributes from a source
        This allows composition rather than inheritance.
    """