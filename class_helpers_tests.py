from collections import namedtuple, Sized, Iterable, Container
from class_helpers import class_helper_meta, patches, metaclass, inherits, include
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
        
class test_include(check_multiple_arguments, unittest.TestCase):
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
        class Person(BasePerson, include([FooBase, BarBase])):
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
        class MetaPerson(inherits(BasePerson), include(BarBase), metaclass(type)):
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

if __name__ == '__main__':
    unittest.main()