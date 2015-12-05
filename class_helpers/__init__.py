""" A suite of metaprogramming functions which allow more flexible
    class maniuplation such as mixins and monkey patching, while
    still writing "Pythonic" code.

    Works for standard classes (instances of 'type')
    and abstract base classes (instances of abc.ABCMeta)
"""
__all__ = ['class_helper_meta','patches','includes','inherits','metaclass','py3','decorate']

from abc import ABCMeta
class class_helper_meta(ABCMeta):
    @classmethod
    def _wrap(mcls, name, value_or_array, **dct):
        dct['solo'] = dct.get('solo', False)
        dct['name'] = name

        # Args is either a single value, or an array of values
        try:
            dct['args'] = tuple(value_or_array)
        except TypeError:
            dct['args'] = (value_or_array,)

        cls_name = '%s_surrogate' % name
        surrogate = type.__new__(mcls, cls_name, (), dct)
        return surrogate

    def __new__(mcls, name, surrogates_or_bases, dct):
        bases = []
        surrogates = []
        params = {'name': name, 'dct': dct}
        for item in surrogates_or_bases:
            if isinstance(item, class_helper_meta):
                surrogates.append(item)
            else:
                bases.append(item)
        bases = params['bases'] = tuple(bases)
        surrogates = tuple(surrogates)
        mcls.handle_surrogates(surrogates, params)

        if 'cls' in params:
            cls = params['cls']
        else:
            _mcls_ = '__metaclass__'
            if (_mcls_ in params) and (_mcls_ in dct):
                raise TypeError("The metaclass can only be declared in one place.")
            meta = params.get(_mcls_) or dct.get(_mcls_) or type
            bases = params.get('bases', ())
            name = params['name']
            cls = meta(name, bases, dct)

        return cls

    @classmethod
    def handle_surrogates(mcls, surrogates, params):
        # Go backward in the event of multiple mixins
        # That was the FIRST mixin is what is most recently
        # Upated to the attributes dictionary
        for surrogate in reversed(surrogates):
            if surrogate.solo:
                if len(surrogates) > 1:
                    msg = "Cannot combine %s with any other helpers"
                    raise TypeError(msg % (surrogate,))
            func = getattr(mcls, '_unwrap_%s' % surrogate.name)
            func(surrogate, params)

    def _unwrap_py6(self, params):
        self.handle_surrogates(self.args, params)

    def _unwrap_includes(self, params):
        dct = params['dct']
        for module in reversed(self.args):
            for base in module.__mro__:
                if base is object:
                    continue
                items = base.__dict__.items()
                for key, value in items:
                    dct[key] = value

    def _unwrap_patches(self, params):
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

    def _unwrap_metaclass(self, params):
        (mcls,) = self.args
        params['__metaclass__'] = mcls

    def _unwrap_inherits(self, params):
        if params['bases']:
            msg = "Inconsistent base class layouts."
            raise TypeError(msg)
        params['bases'] = self.args

    def _unwrap_decorate(self, params):
        ''' We create a mock object which behaves like the class.
            Once the class decorator updates the attributes on the 
            mock object, we then merge its __dict__ with params['dct']
        '''
        for decorate in reversed(self.args):
            dct = params['dct']
            setter = object.__setattr__
            getter = object.__getattribute__.__call__
            class Mock(object):
                __slots__ = ('d',)
                def __init__(self):
                    setter(self, 'd', {})

                def __repr__(self):
                    name = getter(self, '__class__').__name__
                    dct = getter(self, 'd')
                    return '%s(%r)' % (name, dct)

                def __setattr__(self, key, value):
                    if key == '__name__':
                        params['name'] = value
                    else:
                        d = getter(self, 'd')
                        d[key] = value

                def __getattribute__(self, key):
                    try:
                        return getter(self, 'd')[key]
                    except KeyError:
                        return getter(self, key)

                @property
                def __dict__(self):
                    return getter(self, 'd').copy()

            mock = Mock()
            old = dict(mock.__dict__)
            decorate(mock)
            new = dict(mock.__dict__)

            dual = set(new) & set(old)
            deleted_keys = set(old) - set(new)
            created_keys = set(new) - set(old)
            changed_keys = {k for k in dual if new[k] != old[k]}

            for key in (deleted_keys & set(dct)):
                del dct[key]
            for key in (created_keys | changed_keys):
                dct[key] = new[key]

def patches(value_or_array):
    """ Allows for inline monkey patching of classes

        Point = collections.namedtuple('Point',('x','y'))
        original_class = Point
        class Point(patches(point)):
            def __abs__(self):
                return (self.x**2 + self.y**2) ** 0.5

        assert Point is orinal_class #True
    """
    return class_helper_meta._wrap('patches', value_or_array, solo=True)

def includes(value_or_array):
    """ Allows simple inline composition at class delaration time.

        class Toyota(Car, includes(Warranty)):
            pass

        issubclass(Toyota, Car) # True
        issubclass(Toyota, Warranty) # False
    """
    return class_helper_meta._wrap('includes', value_or_array)

def metaclass(value_or_array):
    """ Allows consistent syntax for code shared betwen Python 2 and 3.

        class Python2(A, B):
            __metaclass__ = ABCMeta

        class Python3(A, B, metaclass=ABCMeta):
            pass

        class WorksOnBoth(A, B, metaclass(ABCMeta)):
            pass

        If your bases classes cause a layout conflict,
        please use the "inherits" helper method, py2, or py3

        class Py2_Example(py2(A, B)):
            __metaclass__ = ABCMeta

        class Py3_Example(py3(A, B, metaclass=ABCMeta)):
            pass


    """
    return class_helper_meta._wrap('metaclass', value_or_array)

def inherits(value_or_array):
    """ Resolves any sporadic layout conflices in the metaclass helper
        class Fixed(inherits([A,B]), metaclass(ABCMeta)):
            pass
    """
    return class_helper_meta._wrap('inherits', value_or_array)

def decorate(value_or_array):
    """ Wraps a class decorator and gets it to run BEFORE the class is returned.

        from functools import wraps
        class Foo:
            ''' foo doc '''
            x = 3

        class Bar(decorate(wraps(Foo))):
            ''' bar doc '''
            x = 4

        assert Foo.__name__ == 'Bar'
        assert Foo.__doc__ == 'bar doc'
        assert Foo.x == 4 # functools.wraps does not change this attribute
    """
    return class_helper_meta._wrap('decorate', value_or_array)

def py3(*bases, **dct):
    """ Allows Python3 syntax to be ported into Python2 class definitions.
        class Person(py3(A, B, metaclass=ABCMeta)):
            pass
    """
    return py6(*bases, **dct)

def py2(*bases, **dct):
    """ Allows Python2 syntax to be ported into Python3 class definitions.
        class Person(py2(A, B)):
            __metaclass__ = ABCMeta
    """
    return py6(*bases, **dct)

def py6(*bases, **dct):
    args = []
    if bases:
        args.append(inherits(bases))
    if 'metaclass' in dct:
        args.append(metaclass(dct['metaclass']))
    if 'includes' in dct:
        args.append(includes(dct['includes']))
    return class_helper_meta._wrap('py6', tuple(args), solo=True)
