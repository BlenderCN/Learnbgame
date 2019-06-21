# Copyright (C) 2018 Christopher Gearhart
# chris@bblanimation.com
# http://bblanimation.com/
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# System imports
import json
import itertools
import operator
import hashlib
import numpy as np

# Blender imports
# NONE!


#################### LISTS ####################


# USE EXAMPLE: idfun=(lambda x: x.lower()) so that it ignores case
# https://www.peterbe.com/plog/uniqifiers-benchmark
def uniquify(seq:iter, idfun=None):
    # order preserving
    if idfun is None:
        def idfun(x):
            return x
    seen = {}
    result = []
    for item in seq:
        marker = idfun(item)
        # in old Python versions:
        # if seen.has_key(marker)
        # but in new ones:
        if marker in seen:
            continue
        seen[marker] = 1
        result.append(item)
    return result


# Not order preserving
def uniquify1(seq:iter):
    keys = {}
    for e in seq:
        keys[e] = 1
    return list(keys.keys())

def uniquify2(seq:list, innerType:type=list):
    return [innerType(x) for x in set(tuple(x) for x in seq)]


# efficient removal from list if unordered
def remove_item(ls:list, item):
    try:
        i = ls.index(item)
    except ValueError:
        return False
    ls[-1], ls[i] = ls[i], ls[-1]
    ls.pop()
    return True


# code from https://stackoverflow.com/questions/1518522/python-most-common-element-in-a-list
def most_common(L:list):
    """ find the most common item in a list """
    # get an iterable of (item, iterable) pairs
    SL = sorted((x, i) for i, x in enumerate(L))
    # print 'SL:', SL
    groups = itertools.groupby(SL, key=operator.itemgetter(0))

    # auxiliary function to get "quality" for an item
    def _auxfun(g):
        item, iterable = g
        count = 0
        min_index = len(L)
        for _, where in iterable:
            count += 1
            min_index = min(min_index, where)
        # print 'item %r, count %r, minind %r' % (item, count, min_index)
        return count, -min_index

    # pick the highest-count/earliest item
    return max(groups, key=_auxfun)[0]


def checkEqual(lst:list):
    """ verifies that all items in list are the same """
    return lst.count(lst[0]) == len(lst)


def isUnique(lst:list):
    """ verifies that all items in list are unique """
    return np.unique(lst).size == len(lst)


#################### STRINGS ####################


def cap(string:str, max_len:int):
    """ return string whose length does not exceed max_len """
    return string[:max_len] if len(string) > max_len else string


def rreplace(s:str, old:str, new:str, occurrence:int=1):
    """ replace limited occurences of 'old' with 'new' in string starting from end """
    li = s.rsplit(old, occurrence)
    return new.join(li)


def hash_str(string:str):
    return hashlib.md5(string.encode()).hexdigest()


def str_to_bool(s:str):
    if s.lower() == 'true':
        return True
    elif s.lower() == 'false':
        return False
    else:
        raise ValueError("String '%(s)s' could not be evaluated as a bool" % locals())


#################### OTHER ####################


def deepcopy(object):
    """ efficient way to deepcopy json loadable object """
    jsonObj = json.dumps(object)
    newObj = json.loads(jsonObj)
    return newObj


def checkEqual1(iterator):
    iterator = iter(iterator)
    try:
        first = next(iterator)
    except StopIteration:
        return True
    return all(first == rest for rest in iterator)

def checkEqual2(iterator):
   return len(set(iterator)) <= 1

def checkEqual3(lst):
   return lst[1:] == lst[:-1]
# The difference between the 3 versions are that:
#
# In checkEqual2 the content must be hashable.
# checkEqual1 and checkEqual2 can use any iterators, but checkEqual3 must take a sequence input, typically concrete containers like a list or tuple.
# checkEqual1 stops as soon as a difference is found.
# Since checkEqual1 contains more Python code, it is less efficient when many of the items are equal in the beginning.
# Since checkEqual2 and checkEqual3 always perform O(N) copying operations, they will take longer if most of your input will return False.
# checkEqual2 and checkEqual3 can't be easily changed to adopt to compare a is b instead of a == b.


def confirmList(object):
    """ if single item passed, convert to list """
    if type(object) not in (list, tuple):
        object = [object]
    return object


def confirmIter(object):
    """ if single item passed, convert to list """
    try:
        iter(object)
    except TypeError:
        object = [object]
    return object


class Suppressor(object):
    """ silence function and prevent exceptions """
    def __enter__(self):
        self.stdout = sys.stdout
        sys.stdout = self
    def __exit__(self, type, value, traceback):
        sys.stdout = self.stdout
        if type is not None:
            # Uncomment next line to do normal exception handling
            # raise
            pass
    def write(self, x):
        pass
