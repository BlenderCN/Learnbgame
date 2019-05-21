#  ***** BEGIN GPL LICENSE BLOCK *****
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#  ***** END GPL LICENSE BLOCK *****

import traceback

def copyattrs(src, dst, filter=""):
    for attr in dir(src):
        if attr.find(filter) > -1:
            try:
                setattr(dst, attr, getattr(src, attr))
            except:
                pass

def attrs_to_dict(obj):
    return {name:getattr(obj, name) for name in dir(obj) if not name.startswith("_")}

def dict_to_attrs(obj, d):
    for name, value in d.items():
        if not name.startswith("_"):
            try:
                setattr(obj, name, value)
            except:
                pass

def compare_epsilon(a, b, epsilon):
    if (epsilon is None) or (not isinstance(a, (int, float))): return (a == b)
    return abs(a - b) <= epsilon

def setattr_cmp(obj, name, value, epsilon=None):
    "Utility function to avoid triggering updates when nothing changed"
    if compare_epsilon(getattr(obj, name), value, epsilon): return False
    setattr(obj, name, value)
    return True

def setitem_cmp(obj, key, value, epsilon=None):
    "Utility function to avoid triggering updates when nothing changed"
    try:
        if compare_epsilon(obj[name], value, epsilon): return False
    except KeyError:
        pass
    obj[name] = value
    return True

def bools_to_int(bools):
    # https://stackoverflow.com/questions/4065737/python-numpy-convert-list-of-bools-to-unsigned-int
    return sum((1 << i) for i, b in enumerate(bools) if b)

def binary_search(seq, t, key=None, cmp=None): # bisect module doesn't support key/compare callbacks
    # http://code.activestate.com/recipes/81188-binary-search/
    min = 0
    max = len(seq) - 1
    if not (cmp or key):
        while True:
            if max < min: return -1
            m = (min + max) // 2
            k = seq[m]
            if k < t: min = m + 1
            elif k > t: max = m - 1
            else: return m
    elif key:
        t = key(t)
        while True:
            if max < min: return -1
            m = (min + max) // 2
            k = key(seq[m])
            if k < t: min = m + 1
            elif k > t: max = m - 1
            else: return m
    else:
        while True:
            if max < min: return -1
            m = (min + max) // 2
            s = cmp(seq[m], t)
            if s < 0: min = m + 1
            elif s > 0: max = m - 1
            else: return m

def reverse_enumerate(l):
    return zip(range(len(l)-1, -1, -1), reversed(l))

def next_catch(iterator):
    try:
        return (next(iterator), True)
    except StopIteration as exc:
        return (exc.value, False)

def send_catch(iterator, arg):
    try:
        return (iterator.send(arg), True)
    except StopIteration as exc:
        return (exc.value, False)

def ensure_baseclass(cls, base):
    for _base in cls.__bases__:
        if issubclass(_base, base): return cls
    
    # A declaration like SomeClass(object, object_descendant)
    # will result in an error (cannot create a consistent
    # method resolution order for these bases)
    bases = [b for b in cls.__bases__ if not (b is object)]
    bases.append(base)
    
    return type(cls.__name__, tuple(bases), dict(cls.__dict__))

def issubclass_safe(value, classinfo):
    return (issubclass(value, classinfo) if isinstance(value, type) else None)

def sequence_compare(seqA, seqB):
    if len(seqA) != len(seqB): return False
    return all(seqA[i] == seqB[i] for i in range(len(seqA)))

def sequence_startswith(a, b):
    na = len(a); nb = len(b)
    if nb > na: return False
    return all(a[i] == b[i] for i in range(nb))

def sequence_endswith(a, b):
    na = len(a); nb = len(b)
    if nb > na: return False
    return all(a[na-i] == b[nb-i] for i in range(1, nb+1))

# Primary function of such objects is to store
# attributes and values assigned to an instance
class AttributeHolder:
    def __init__(self, *args, **kwargs):
        self.__original = (args[0] if args else None)
        for k, v in kwargs.items():
            setattr(self, k, v)
    
    def __getattr__(self, key):
        # This is primarily to be able to have some default values
        if self.__original: return getattr(self.__original, key)
        raise AttributeError("attribute '%s' is not defined" % key)
    
    def __getitem__(self, key):
        try:
            return self.__items[key]
        except AttributeError:
            raise KeyError(key)
    
    def __setitem__(self, key, value):
        try:
            self.__items[key] = value
        except AttributeError:
            self.__items = {key:value}
    
    def __delitem__(self, key):
        try:
            del self.__items[key]
        except AttributeError:
            raise KeyError(key)

class DummyObject:
    def __call__(self, *args, **kwargs):
        return self
    def __getattr__(self, name):
        return self
    def __setattr__(self, name, value):
        pass
    def __getitem__(self, key):
        return self
    def __setitem__(self, key, value):
        pass
    def __delitem__(self, key):
        pass

class SilentError:
    """
    A syntactic-sugar construct for reporting errors
    in code that isn't expected to raise any exceptions.
    This is primarily used in continuously invoked methods
    like drawing callbacks and modal operators.
    Reasons: to avoid error reports from constantly
    popping up (as in case of UI/operators); to avoid
    messing up OpenGL states if exception occurred
    somewhere in the middle of drawing code.
    Also, some some operations like generator.send()
    seem to "swallow" exceptions and turn them
    into StopIteration (without printing the cause).
    """
    
    def __init__(self, catch=Exception):
        if not isinstance(catch, (type, tuple)):
            if hasattr(catch, "__iter__"):
                catch = tuple(catch)
            else:
                catch = type(None)
        self.catch = catch
        self.value = None
    
    def __enter__(self):
        pass
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        if not isinstance(exc_value, self.catch): return
        self.value = exc_value
        print("".join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
        return True

class PrimitiveLock(object):
    "Primary use of such lock is to prevent infinite recursion"
    def __init__(self):
        self.count = 0
    def __bool__(self):
        return bool(self.count)
    def __enter__(self):
        self.count += 1
    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.count -= 1
