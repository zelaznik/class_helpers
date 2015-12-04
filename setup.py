from distutils.core import setup

def test():
  import unittest
  import tests
  unittest.main()

setup(
    name     = 'class_helpers',
    version  = '1.0',
    url      = 'https://github.com/zelaznik/class_helpers',
    author       = 'Steve Zelaznik',
    author_email = 'steve.zelaznik@gmail.com',

    description = """Allows monkey patching, mixins, composition, and more, all within Pythonic syntax.""",

    packages = ['class_helpers'],
    license  = 'MIT License',
    test_suite = 'tests',
    cmds = {
      'test': test
    }
)