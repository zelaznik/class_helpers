# Class Helpers

## Overview
- A set of metaprogramming patterns to allow more flexible class manipulation, but with Pythonic syntax.
- Allows metaclasses to be declared in a neat consistent syntax for both Python 2 and 3
- Allows monkey patching of existing classes.
- Useful for customizing output from factory functions such as namedtuple.

## How It Works
- The helper methods return an instance of a special surrogate metaclass.
- The regular class that is declared will attempt to create a subclass of those surrogates.
- The __new__ method of the surrogate class has logic so that your normal class is returne

## Available Methods

### metaclass:
#### For consistent metaclass Syntax between Python 2 and 3

```python
class WorksInPython2(A, B):
    __metaclass__ = ABCMeta

class WorksInPython3(A, B, metaclass=ABCMeta):
    pass

from class_helpers import metaclass
class WorksForBoth(A, B, metaclass(ABCMeta)):
    pass
```

### py3:
#### Allows pure Python3 metaclass syntax to be ported into Python3

```python
class WrapArgs(py3(A, B, metaclass=ABCMeta)):
    pass

# Can also mixin modules using keywords
class WrapArgs(py3(A, B, includes=Enumerable, metaclass=ABCMeta)):
    pass
```

### inherits
##### For resolving layout conflicts caused by the metaclass helper

```python
class Fixed(inherits([A,B]), metaclass(ABCMeta)):
    pass
```

### patches
##### Allows inline monkey patching of existing classes

```python
Point = collections.namedtuple('Point',('x','y'))
original_class = Point
class Point(patches(Point)):
    def __abs__(self):
        return (self.x**2 + self.y**2) ** 0.5

assert Point is original_class #True
```

### includes
##### Composition not inheritence.  Attributes from another class are copied and mixed in.

```python
class Toyota(Car, includes(Warranty)):
    pass

issubclass(Toyota, Car) # True
issubclass(Toyota, Warranty) # False
```
