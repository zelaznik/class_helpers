# Class Helpers
- A set of metaprogramming patterns to allow more flexible class manipulation, but with Pythonic syntax.

## class_helpers.metaclass
##### For consistent metaclass Syntax between Python 2 and 3

```python
class WorksInPython2(A, B):
    __metaclass__ = ABCMeta

class WorksInPython3(A, B, metaclass=ABCMeta):
    pass

from class_helpers import metaclass
class WorksForBoth(A, B, metaclass(ABCMeta)):
    pass
```

## class_helpers.patches
##### Allows inline monkey patching of existing classes

```python
from collections import namedtuple
Point = namedtuple('Point',('x','y'))
class Point(patches(Point)):
    def __abs__(self):
        return (self.x**2+self.y**2)**0.5
```
