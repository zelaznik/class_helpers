import unittest
from collections import namedtuple
from class_helpers import patches

class test_patches(unittest.TestCase):
    def setUp(self):
        Person = namedtuple('Person',('first_name','last_name'))
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
        del self.Person, self.p

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
        
if __name__ == '__main__':
    unittest.main()