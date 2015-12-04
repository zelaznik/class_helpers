import unittest
from collections import namedtuple, Sized, Iterable, Container
from class_helpers import patches, metaclass, inherits
from operator import itemgetter
from abc import ABCMeta

class test_metaclass(unittest.TestCase):
    def make_person(self):
        self.surrogate = metaclass(ABCMeta)
        class Person(self.surrogate):
            def __init__(self, first_name, last_name):
                self.first_name = first_name
                self.last_name = last_name
            def full_name(self):
                return ', '([self.last_name, self.first_name])
        self.Person = Person
        
    def setUp(self):
        self.make_person()
        self.p = self.Person('Steve','Zelaznik')
        
    def tearDown(self):
        del self.Person, self.p, self.surrogate

    def test_metaclass_assigned_correctly(self):
        self.assertIs(type(self.Person), ABCMeta)

class test_inherits(unittest.TestCase):
    def make_person(self):
        self.surrogate = inherits(Sized, Iterable, Container)
        class Person(self.surrogate):
            first_name = property(itemgetter(0))
            last_name = property(itemgetter(1))
            def __init__(self, *args):
                self.arr = args
            def __getitem__(self, index):
                return self.arr[index]
            def __len__(self):
                return len(self.arr)
            def __iter__(self):
                return iter(self.arr)
            def __contains__(self, value):
                return value in self.arr
        self.Person = Person
                
    def setUp(self):
        self.make_person()
        self.p = self.Person('Steve','Zelaznik')
        
    def tearDown(self):
        del self.Person
        
    def test_inherits_class_bases_are_correct(self):
        self.assertEqual(self.Person.__bases__, (Sized,Iterable,Container))
        
    def test_inherits_attributes_read_correctly_first_name(self):
        self.assertEqual(self.p.first_name, 'Steve')

    def test_inherits_attributes_read_correctly_last_name(self):
        self.assertEqual(self.p.last_name, 'Zelaznik')
        
    def test_inherits_attributes_read_correctly_length(self):
        self.assertEqual(len(self.p), 2)

    def test_inherits_attributes_read_correctly_iter(self):
        self.assertEqual(list(self.p), ['Steve','Zelaznik'])
        
    def test_inherits_attributes_read_correctly_contains(self):
        self.assertIn('Steve', self.p)
        self.assertNotIn('blah', self.p)

class test_patches(unittest.TestCase):
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
        self.assertRaises(ValueError, try_bad_name)
        
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