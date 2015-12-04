from class_helpers import class_helper_meta, patches, decorate
from class_helpers import metaclass, inherits, includes, py3
from collections import namedtuple, Sized, Iterable, Container
from abc import ABCMeta, abstractmethod
from operator import itemgetter
import unittest

class BasePerson(object):
    def __init__(self, *args):
        self.args = args
    def __len__(self):
        return len(self.args)
    def __iter__(self):
        return iter(self)
    def __getitem__(self, i):
        return self.args[i]
    def __contains__(self, value):
        return value in self.args
    @property
    def full_name(self):
        return ', '.join([self.last_name, self.first_name])

class check_multiple_arguments(object):
    def subclass(self):
        raise NotImplementedError

    class A(object):
        pass
    class B(object):
        pass
    class C(object):
        pass

    def test_parses_single_argument(self):
        A, B, C = self.A, self.B, self.C
        surrogate = self.subclass(A)
        self.assertEqual(surrogate.args, (A,))
        
    def test_rejects_three_arguments(self):
        A, B, C = self.A, self.B, self.C
        self.assertRaises(TypeError, self.subclass, A, B, C)

    def test_parses_array_with_single_argument(self):
        A, B, C = self.A, self.B, self.C
        surrogate = self.subclass([A])
        self.assertEqual(surrogate.args, (A,))

    def test_parses_array_with_multiple_arguments(self):
        A, B, C = self.A, self.B, self.C
        surrogate = self.subclass([A,B,C])
        self.assertEqual(surrogate.args, (A,B,C))

class test_metaclass(unittest.TestCase):
    subclass = staticmethod(metaclass)

    class MyMeta(ABCMeta):
        pass

    BasePerson = BasePerson

    def make_person(self):
        surrogate = self.surrogate = metaclass(ABCMeta)
        class Person(self.BasePerson, Sized, Iterable, Container, surrogate):
            pass
        self.Person = Person
        
    def setUp(self):
        self.make_person()
        self.p = self.Person('Steve','Zelaznik')
        
    def tearDown(self):
        del self.Person, self.p, self.surrogate

    def test_metaclass_assigned_correctly(self):
        self.assertIs(type(self.Person), ABCMeta)
        
    def test_bases_are_assigned_properly(self):
        expected = (self.BasePerson,Sized,Iterable,Container)
        self.assertEqual(self.Person.__bases__,expected)
        
class test_metaclass_with_inheritance_wrapper(check_multiple_arguments, unittest.TestCase):
    subclass = staticmethod(metaclass)
    def make_person(self):
        self.surrogate = metaclass(ABCMeta)
        bases = inherits(self.BasePerson, Sized, Iterable, Container)
        class Person(bases, metaclass(ABCMeta)):
            pass
        self.Person = Person
        
class test_includes(check_multiple_arguments, unittest.TestCase):
    subclass = staticmethod(metaclass)
    def setUp(self):
        class Base(ABCMeta('ABC',(),{})):
            first_name = 'Base First'
            last_name = 'Base Last'
            x,y = 3,4
        class FooBase(Base):
            last_name = 'FooBase Last'
            z = 5
        class BarBase(Base):
            z = 7
        class Foo(FooBase):
            x, y = 0,-1
        class Bar(BarBase):
            x, y = -1, 8
        class Person(BasePerson, includes([FooBase, BarBase])):
            first_name = property(itemgetter(0))
            last_name = property(itemgetter(1))
            def __init__(self, first_name, last_name):
                self.arr = [first_name, last_name]
            def __getitem__(self, i):
                return self.arr[i]
            def __repr__(self):
                return '%s, %s' % (self.last_name, self.first_name)
        class Expected(BasePerson, FooBase, BarBase):
            pass
        class MetaPerson(inherits(BasePerson), includes(BarBase), metaclass(type)):
            pass
        self.Expected = Expected
        self.Person = Person
        self.FooBase = FooBase
        self.BarBase = BarBase
        self.p = self.Person('Steve','Zelaznik')
        self.e = self.Expected("Steve",'Zelaznik')

    def test_mixins_override_inheritence(self):
        self.assertEqual(self.p.first_name, 'Base First')
        
    def test_left_mixins_have_priority(self):
        self.assertEqual(self.p.last_name, 'Base Last')
        
    def test_object_does_not_inherit_foo_base(self):
        self.assertNotIn(self.FooBase, self.Person.__mro__)
    
    def test_object_does_not_inherit_bar_base(self):
        self.assertNotIn(self.BarBase, self.Person.__mro__)
    
    def test_attribute_x_equivalent_value_to_inheritance(self):
        self.assertEqual(self.p.x, self.e.x)

    def test_attribute_y_equivalent_value_to_inheritance(self):
        self.assertEqual(self.p.y, self.e.y)

    def test_attribute_z_equivalent_value_to_inheritance(self):
        self.assertEqual(self.p.z, self.e.z)

class test_patches_raises_error_with_other_helpers(unittest.TestCase):
    def test_patches_raises_error_with_metaclass(self):
        def attempt():
            class Thing(object):
                pass
            class Thing(patches(Thing),metaclass(type)):
                pass
        self.assertRaises(TypeError, attempt)

    def test_patches_raises_error_with_inherits(self):
        def attempt():
            class Thing(object):
                pass
            class Thing(patches(Thing),inherits(object)):
                pass
        self.assertRaises(TypeError, attempt)

    def test_patches_raises_error_with_includes(self):
        def attempt():
            class Thing(object):
                pass
            class Thing(patches(Thing),includes(object)):
                pass
        self.assertRaises(TypeError, attempt)

class test_patches(check_multiple_arguments, unittest.TestCase):
    subclass = staticmethod(metaclass)
    @staticmethod
    def make_person():
        return namedtuple('Person',('first_name','last_name'))

    def setUp(self):
        Person = self.make_person()
        self.p = Person('Steve','Zelaznik')
        self.surrogate = patches(Person)
        self.original_class = Person
        self.orig_attrs = {k: getattr(Person, k) for k in dir(Person)}
        class Person(self.surrogate):
            def __repr__(self):
                return "Hello"
        self.Person = Person
        self.new_attrs = {k: getattr(Person, k) for k in dir(Person)}

    def tearDown(self):
        del self.Person, self.p, self.surrogate
        del self.original_class
        del self.orig_attrs, self.new_attrs

    def test_patched_class_reflects_updated_method(self):
        self.assertEqual(repr(self.p), "Hello")
        
    def test_patched_class_does_not_modify_anything_else(self):
        expected_differences = {'__repr__'}
        orig, new = self.orig_attrs, self.new_attrs
        keys = set(orig) | set(new)
        actual_differences = {k for k in keys if orig[k] != new[k]}
        self.assertEqual(expected_differences, actual_differences)            
        
    def test_patched_class_does_not_make_a_copy(self):
        self.assertIs(self.Person, self.original_class)
        
    def test_patches_requires_patched_name_to_eq_orig_name(self):
        def try_bad_name():
            class WrongName(self.surrogate):
                pass
        self.assertRaises(TypeError, type, 'WrongName', (self.surrogate,), {})
        self.assertRaises(TypeError, try_bad_name)
        
class test_patches_for_ABCMeta(test_patches):
    @staticmethod
    def make_person():
        ABC = ABCMeta('ABC',(), {})
        class Person(ABC):
            def __init__(self, first_name, last_name):
                self.first_name = first_name
                self.last_name = last_name
        return Person

class test_patches_for_arbitrary_metaclass(test_patches):
    @staticmethod
    def make_person():
        class ArbitraryMeta(type):
            pass
        Arbitrary = ArbitraryMeta('Arbitrary',(),{})
        class Person(Arbitrary):
            def __init__(self, first_name, last_name):
                self.first_name = first_name
                self.last_name = last_name
        return Person

class test_py3(unittest.TestCase):
    def setUp(self):
        class Enumerable(object):
            x,y,z = 3,4,5
        class A(object):
            a = 0
            x = -1
        class B(object):
            a = 1
        surrogate = py3(A, B, metaclass=ABCMeta, includes=[Enumerable])
        class C(surrogate):
            pass
        self.Enumerable = Enumerable
        self.A, self.B, self.C = A, B, C
        self.surrogate = surrogate

    def tearDown(self):
        del self.Enumerable, self.surrogate, self.A, self.B, self.C

    def test_class_C_inherits_from_A(self):
        self.assertTrue(issubclass(self.C, self.A))

    def test_class_C_inherits_from_B(self):
        self.assertTrue(issubclass(self.C, self.B))

    def test_values_from_A_override_B(self):
        self.assertEqual(self.C.a, 0)

    def test_class_C_does_NOT_inherit_from_Enumerable(self):
        self.assertFalse(issubclass(self.C, self.Enumerable))

    def test_class_C_references_mixin_value_x(self):
        self.assertEqual(self.C.x, 3)

    def test_class_C_references_mixin_value_y(self):
        self.assertEqual(self.C.y, 4)

    def test_class_C_copies_values_not_references_them(self):
        self.Enumerable.z = 10
        self.assertEqual(self.C.z, 5)

class test_py3_obsure_base_classes(unittest.TestCase):
    def setUp(self):
        class Enumerable(object):
            x,y,z = 3,4,5

        class UberMeta(type):
            pass
        
        A = UberMeta('A',(),{})
        class B(object):
            pass
        self.A, self.B, = A,B
        self.Enumerable = Enumerable
        self.UberMeta = UberMeta
        
    def make_class(self):
        try:
            return self.C
        except AttributeError:
            pass
        A, B, Enumerable = self.A, self.B, self.Enumerable

        class C(py3(A,B,includes=Enumerable)):
            pass

        self.C = C
        return C

    def tearDown(self):
        del self.A, self.B
        del self.Enumerable
        del self.UberMeta
        try:
            del self.C
        except AttributeError:
            pass

    def test_handles_inheritance_with_obscure_metaclass(self):
        cls = self.make_class()
        self.assertTrue(issubclass(cls, (self.A, self.B)))

    def test_assigns_correct_obscure_metaclass(self):
        cls = self.make_class()
        self.assertTrue(isinstance(cls, self.UberMeta))

class test_class_decorator_wrapper(unittest.TestCase):
    def setUp(self):

        class Foo:
            ''' foo doc '''
            x = 3

        def wraps(orig):
            def _wraps(cls):
                cls.__name__ = orig.__name__
                cls.__doc__ = orig.__doc__
                return cls
            return _wraps

        class Bar(decorate(wraps(Foo))):
            ''' bar doc '''
            x = 4



        self.Foo, self.Bar = Foo, Bar

    def tearDown(self):
        del self.Foo, self.Bar

    def test_name_updates(self):
        self.assertEqual(self.Foo.__name__, 'Bar')

    def test_doc_update(self):
        self.assertEqual(self.Foo.__doc__, 'foo doc')

    def decorator_does_not_change_too_much(self):
        self.assertEqual(self.Foo.x, 3)

if __name__ == '__main__':
    unittest.main()