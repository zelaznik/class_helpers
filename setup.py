from distutils.core import setup

setup(
    name     = 'class_helpers',
    version  = '1.0',
    url      = 'https://github.com/zelaznik/class_helpers',

    author       = 'Steve Zelaznik',
    author_email = 'steve.zelaznik@gmail.com',

    packages = ['class_helpers'],
    license  = 'MIT License',

    description = """Allows monkey patching, mixins, composition, and more, all within Pythonic syntax.',
)