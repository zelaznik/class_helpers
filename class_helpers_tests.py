import unittest
from abc import ABCMeta
from collections import namedtuple
from class_helpers import patches, metaclass


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