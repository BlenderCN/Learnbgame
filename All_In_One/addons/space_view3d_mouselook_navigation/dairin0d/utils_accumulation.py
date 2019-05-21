# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy

import math
import bisect

from .utils_python import sequence_startswith, sequence_endswith
from .utils_text import indent, longest_common_substring

#============================================================================#

"""
TODO: "active" query (for consistency)
"""

class Aggregator:
    _count = 0
    _same = True
    _prev = None
    
    _min = None
    _max = None
    
    _sum = None
    _sum_log = None
    _sum_rec = None
    _product = None
    
    _Ak = None
    _Qk = None
    
    _sorted = None
    
    _freq_map = None
    _freq_max = None
    _modes = None
    
    _union = None
    _intersection = None
    _difference = None
    
    _subseq = None
    _subseq_starts = None
    _subseq_ends = None
    
    # sum can be calculated from average, and product (for values > 0)
    # can be calculated from sum_log, but it won't be precise for ints
    
    type = property(lambda self: self._type)
    
    count = property(lambda self: self._count)
    same = property(lambda self: self._same)
    
    min = property(lambda self: self._min)
    max = property(lambda self: self._max)
    @property
    def range(self):
        if (self._max is None) or (self._min is None): return None
        return self._max - self._min
    @property
    def center(self):
        if (self._max is None) or (self._min is None): return None
        return (self._max + self._min) * 0.5
    
    sum = property(lambda self: self._sum)
    sum_log = property(lambda self: self._sum_log)
    sum_rec = property(lambda self: self._sum_rec)
    product = property(lambda self: self._product)
    
    @property
    def mean(self):
        return self._Ak
    @property
    def geometric_mean(self):
        if (self._sum_log is None) or (self._count is None): return None
        return math.exp(self._sum_log / self._count)
    @property
    def harmonic_mean(self):
        if (self._sum_rec is None): return None
        return 1.0 / self._sum_rec
    @property
    def variance(self):
        if (self._Qk is None) or (self._count is None): return None
        if self._count < 2: return 0.0
        return self._Qk / (self._count - 1)
    @property
    def stddev(self):
        if (self._Qk is None) or (self._count is None): return None
        if self._count < 2: return 0.0
        return math.sqrt(self._Qk / (self._count - 1))
    
    sorted = property(lambda self: self._sorted)
    @property
    def median(self):
        if not self._sorted: return None
        n = len(self._sorted)
        if (n % 2) == 1: return self._sorted[n // 2]
        i = n // 2
        return (self._sorted[i] + self._sorted[i - 1]) * 0.5
    
    freq_map = property(lambda self: self._freq_map)
    freq_max = property(lambda self: self._freq_max)
    modes = property(lambda self: self._modes)
    mode = property(lambda self: self._modes[0] if self._modes else None)
    
    union = property(lambda self: self._union)
    intersection = property(lambda self: self._intersection)
    difference = property(lambda self: self._difference)
    
    subseq = property(lambda self: self._subseq)
    subseq_starts = property(lambda self: self._subseq_starts)
    subseq_ends = property(lambda self: self._subseq_ends)
    
    def get(self, query, fallback):
        value = getattr(self, query)
        if value is None: return fallback
        return ((value > 0.5) if isinstance(fallback, bool) else value)
    
    _numerical_queries = frozenset([
        'count', 'same', 'min', 'max', 'range', 'center',
        'sum', 'sum_log', 'sum_rec', 'product',
        'mean', 'geometric_mean', 'harmonic_mean', 'variance', 'stddev',
        'sorted', 'median', 'freq_map', 'freq_max', 'modes',
    ])
    _enum_queries = frozenset([
        'count', 'same',
        'freq_map', 'freq_max', 'modes',
        'union', 'intersection', 'difference',
    ])
    _sequence_queries = frozenset([
        'count', 'same',
        'sorted', 'median', 'freq_map', 'freq_max', 'modes',
        'subseq', 'subseq_starts', 'subseq_ends',
    ])
    _object_queries = frozenset([
        'count', 'same',
        'freq_map', 'freq_max', 'modes',
    ])
    _all_queries = {'NUMBER':_numerical_queries, 'ENUM':_enum_queries,
        'SEQUENCE':_sequence_queries, 'OBJECT':_object_queries}
    
    _compiled = {}
    
    def __init__(self, type, queries=None, convert=None, epsilon=1e-6):
        self._type = type
        
        self._startswith = sequence_startswith
        self._endswith = sequence_endswith
        if type == 'STRING':
            self._startswith = str.startswith
            self._endswith = str.endswith
            type = 'SEQUENCE'
        elif type == 'BOOL':
            if convert is None: convert = int
            type = 'NUMBER'
        
        if queries is None:
            queries = self._all_queries[type]
        elif isinstance(queries, str):
            queries = queries.split(" ")
        
        if (type != 'NUMBER') or ((epsilon is not None) and (epsilon <= 0)): epsilon = None
        
        compiled_key0 = (type, frozenset(queries), convert, epsilon)
        compiled = Aggregator._compiled.get(compiled_key0)
        
        if not compiled:
            queries = set(queries) # make sure it's a copy
            
            # make sure requirements are included
            if 'same' in queries: queries.update(('min', 'max') if epsilon else ('prev',))
            if ('range' in queries) or ('center' in queries): queries.update(('min', 'max'))
            if 'mean' in queries: queries.add('Ak')
            if 'geometric_mean' in queries: queries.update(('sum_log', 'count'))
            if 'harmonic_mean' in queries: queries.add('sum_rec')
            if ('variance' in queries) or ('stddev' in queries): queries.update(('Qk', 'count'))
            if 'Qk' in queries: queries.add('Ak')
            if 'Ak' in queries: queries.add('count')
            if 'median' in queries: queries.add('sorted')
            if 'mode' in queries: queries.add('modes')
            if 'modes' in queries: queries.add('freq_max')
            if 'freq_max' in queries: queries.add('freq_map')
            if queries.intersection(('subseq', 'subseq_starts', 'subseq_ends')):
                queries.update(('subseq', 'subseq_starts', 'subseq_ends'))
            
            compiled_key = (type, frozenset(queries), convert, epsilon)
            compiled = Aggregator._compiled.get(compiled_key)
            
            if not compiled:
                compiled = self._compile(type, queries, convert, epsilon)
                Aggregator._compiled[compiled_key] = compiled
            
            Aggregator._compiled[compiled_key0] = compiled
        
        self.queries = compiled_key0[1] # the original queries, without dependencies
        
        # Assign bound methods
        self.reset = compiled[0].__get__(self, self.__class__)
        self._init = compiled[1].__get__(self, self.__class__)
        self._add = compiled[2].__get__(self, self.__class__)
        
        self.reset()
    
    def _compile(self, type, queries, convert, epsilon):
        reset_lines = []
        init_lines = []
        add_lines = []
        
        localvars = dict(log=math.log, insort_left=bisect.insort_left,
            startswith=self._startswith, endswith=self._endswith, convert=convert)
        
        if 'count' in queries:
            reset_lines.append("self._count = 0")
            init_lines.append("self._count = 1")
            add_lines.append("self._count += 1")
        
        if 'min' in queries:
            reset_lines.append("self._min = None")
            init_lines.append("self._min = value")
            add_lines.append("self._min = min(self._min, value)")
        if 'max' in queries:
            reset_lines.append("self._max = None")
            init_lines.append("self._max = value")
            add_lines.append("self._max = max(self._max, value)")
        
        if 'same' in queries:
            reset_lines.append("self._same = True")
            init_lines.append("self._same = True")
            if epsilon:
                add_lines.append("if self._same: self._same = (abs(self._max - self._min) <= %s)" % epsilon)
            else:
                add_lines.append("if self._same: self._same = (value == self._prev)")
        if 'prev' in queries:
            reset_lines.append("self._prev = None")
            init_lines.append("self._prev = value")
            add_lines.append("self._prev = value")
        
        if 'sum' in queries:
            reset_lines.append("self._sum = None")
            init_lines.append("self._sum = value")
            add_lines.append("self._sum += value")
        if 'sum_log' in queries:
            reset_lines.append("self._sum_log = None")
            init_lines.append("self._sum_log = (log(value) if value > 0.0 else 0.0)")
            add_lines.append("self._sum_log += (log(value) if value > 0.0 else 0.0)")
        if 'sum_rec' in queries:
            reset_lines.append("self._sum_rec = None")
            init_lines.append("self._sum_rec = (1.0 / value if value != 0.0 else 0.0)")
            add_lines.append("self._sum_rec += (1.0 / value if value != 0.0 else 0.0)")
        if 'product' in queries:
            reset_lines.append("self._product = None")
            init_lines.append("self._product = value")
            add_lines.append("self._product *= value")
        
        if 'Ak' in queries:
            reset_lines.append("self._Ak = None")
            init_lines.append("self._Ak = value")
            add_lines.append("delta = (value - self._Ak)")
            add_lines.append("self._Ak += delta / self._count")
        if 'Qk' in queries:
            reset_lines.append("self._Qk = None")
            init_lines.append("self._Qk = 0.0")
            add_lines.append("self._Qk += delta * (value - self._Ak)")
        
        if 'sorted' in queries:
            reset_lines.append("self._sorted = None")
            init_lines.append("self._sorted = [value]")
            add_lines.append("insort_left(self._sorted, value)")
        
        if type != 'ENUM':
            if 'freq_map' in queries:
                reset_lines.append("self._freq_map = None")
                init_lines.append("self._freq_map = {value:1}")
                add_lines.append("freq = self._freq_map.get(value, 0) + 1")
                add_lines.append("self._freq_map[value] = freq")
            if 'freq_max' in queries:
                reset_lines.append("self._freq_max = None")
                init_lines.append("self._freq_max = 0")
                add_lines.append("if freq > self._freq_max:")
                add_lines.append("    self._freq_max = freq")
            if 'modes' in queries:
                reset_lines.append("self._modes = None")
                init_lines.append("self._modes = [value]")
                add_lines.append("    self._modes = [value]")
                add_lines.append("elif freq == self._freq_max:")
                add_lines.append("    self._modes.append(value)")
        else:
            if 'freq_map' in queries:
                reset_lines.append("self._freq_map = None")
                init_lines.append("self._freq_map = {item:1 for item in value}")
                add_lines.append("for item in value:")
                add_lines.append("    freq = self._freq_map.get(item, 0) + 1")
                add_lines.append("    self._freq_map[item] = freq")
            if 'freq_max' in queries:
                reset_lines.append("self._freq_max = None")
                init_lines.append("self._freq_max = 0")
                add_lines.append("    if freq > self._freq_max:")
                add_lines.append("        self._freq_max = freq")
            if 'modes' in queries:
                reset_lines.append("self._modes = None")
                init_lines.append("self._modes = list(value)")
                add_lines.append("        self._modes = [item]")
                add_lines.append("    elif freq == self._freq_max:")
                add_lines.append("        self._modes.append(item)")
        
        if 'union' in queries:
            reset_lines.append("self._union = None")
            init_lines.append("self._union = set(value)")
            add_lines.append("self._union.update(value)")
        if 'intersection' in queries:
            reset_lines.append("self._intersection = None")
            init_lines.append("self._intersection = set(value)")
            add_lines.append("self._intersection.intersection_update(value)")
        if 'difference' in queries:
            reset_lines.append("self._difference = None")
            init_lines.append("self._difference = set(value)")
            add_lines.append("self._difference.symmetric_difference_update(value)")
        
        if 'subseq' in queries:
            reset_lines.append("self._subseq = None")
            reset_lines.append("self._subseq_starts = None")
            reset_lines.append("self._subseq_ends = None")
            init_lines.append("self._subseq = value")
            init_lines.append("self._subseq_starts = True")
            init_lines.append("self._subseq_ends = True")
            add_lines.append("self._subseq_update(value)")
        
        reset_lines.append("self.add = self._init")
        reset_lines = [indent(line, "    ") for line in reset_lines]
        reset_lines.insert(0, "def reset(self):")
        reset_code = "\n".join(reset_lines)
        #print(reset_code)
        exec(reset_code, localvars, localvars)
        reset = localvars["reset"]
        
        if convert is not None: init_lines.insert(0, "value = convert(value)")
        init_lines.append("self.add = self._add")
        init_lines = [indent(line, "    ") for line in init_lines]
        init_lines.insert(0, "def _init(self, value):")
        init_code = "\n".join(init_lines)
        #print(init_code)
        exec(init_code, localvars, localvars)
        _init = localvars["_init"]
        
        if convert is not None: init_lines.insert(0, "value = convert(value)")
        add_lines = [indent(line, "    ") for line in add_lines]
        add_lines.insert(0, "def _add(self, value):")
        add_code = "\n".join(add_lines)
        #print(add_code)
        exec(add_code, localvars, localvars)
        _add = localvars["_add"]
        
        return reset, _init, _add
    
    def _subseq_update(self, value):
        if self._subseq_starts:
            if self._startswith(value, self._subseq):
                pass
            elif self._startswith(self._subseq, value):
                self._subseq = value
            else:
                self._subseq_starts = False
        if self._subseq_ends:
            if self._endswith(value, self._subseq):
                pass
            elif self._endswith(self._subseq, value):
                self._subseq = value
            else:
                self._subseq_ends = False
        if self._subseq and not (self._subseq_starts or self._subseq_ends):
            prev_subseq = self._subseq
            self._subseq = next(iter(longest_common_substring(self._subseq, value)), None) or value[0:0]
            # Seems like there is no other way than to check everything again
            # (e.g. Blue, Red, White -> "e" is common, but is wasn't on the end in "Red")
            #if self._subseq:
            #    if self._startswith(prev_subseq, self._subseq):
            #        self._subseq_starts = self._startswith(value, self._subseq)
            #    if self._endswith(prev_subseq, self._subseq):
            #        self._subseq_ends = self._endswith(value, self._subseq)

class VectorAggregator:
    def __init__(self, size, type, queries=None, covert=None, epsilon=1e-6):
        self._type = type
        self.axes = tuple(Aggregator(type, queries, covert, epsilon) for i in range(size))
    
    def reset(self):
        for axis in self.axes:
            axis.reset()
    
    def __len__(self):
        return len(self.axes)
    
    def add(self, value, i=None):
        if i is None:
            for axis, item in zip(self.axes, value):
                axis.add(item)
        else:
            self.axes[i].add(value)
    
    type = property(lambda self: self._type)
    
    count = property(lambda self: (self.axes[0].count if self.axes else 0)) # same for all
    same = property(lambda self: tuple(axis.same for axis in self.axes))
    
    min = property(lambda self: tuple(axis.min for axis in self.axes))
    max = property(lambda self: tuple(axis.max for axis in self.axes))
    range = property(lambda self: tuple(axis.range for axis in self.axes))
    center = property(lambda self: tuple(axis.center for axis in self.axes))
    
    sum = property(lambda self: tuple(axis.sum for axis in self.axes))
    sum_log = property(lambda self: tuple(axis.sum_log for axis in self.axes))
    sum_rec = property(lambda self: tuple(axis.sum_rec for axis in self.axes))
    product = property(lambda self: tuple(axis.product for axis in self.axes))
    
    mean = property(lambda self: tuple(axis.mean for axis in self.axes))
    geometric_mean = property(lambda self: tuple(axis.geometric_mean for axis in self.axes))
    harmonic_mean = property(lambda self: tuple(axis.harmonic_mean for axis in self.axes))
    variance = property(lambda self: tuple(axis.variance for axis in self.axes))
    stddev = property(lambda self: tuple(axis.stddev for axis in self.axes))
    
    sorted = property(lambda self: tuple(axis.sorted for axis in self.axes))
    median = property(lambda self: tuple(axis.median for axis in self.axes))
    
    freq_map = property(lambda self: tuple(axis.freq_map for axis in self.axes))
    freq_max = property(lambda self: tuple(axis.freq_max for axis in self.axes))
    modes = property(lambda self: tuple(axis.modes for axis in self.axes))
    mode = property(lambda self: tuple(axis.mode for axis in self.axes))
    
    union = property(lambda self: tuple(axis.union for axis in self.axes))
    intersection = property(lambda self: tuple(axis.intersection for axis in self.axes))
    difference = property(lambda self: tuple(axis.difference for axis in self.axes))
    
    subseq = property(lambda self: tuple(axis.subseq for axis in self.axes))
    subseq_starts = property(lambda self: tuple(axis.subseq_starts for axis in self.axes))
    subseq_ends = property(lambda self: tuple(axis.subseq_ends for axis in self.axes))
    
    def get(self, query, fallback, vector=True):
        if not vector: return tuple(axis.get(query, fallback) for axis in self.axes)
        return tuple(axis.get(query, fb_item) for axis, fb_item in zip(self.axes, fallback))

class PatternRenamer:
    before = "\u2190"
    after = "\u2192"
    whole = "\u2194"
    
    @classmethod
    def is_pattern(cls, value):
        return (cls.before in value) or (cls.after in value) or (cls.whole in value)
    
    @classmethod
    def make(cls, subseq, subseq_starts, subseq_ends):
        pattern = subseq
        if (not subseq_starts): pattern = cls.before + pattern
        if (not subseq_ends): pattern = pattern + cls.after
        if (pattern == cls.before+cls.after): pattern = cls.whole
        return pattern
    
    @classmethod
    def apply(cls, value, src_pattern, pattern):
        middle = src_pattern.lstrip(cls.before).rstrip(cls.after).rstrip(cls.whole)
        if middle not in value: return value # pattern not applicable
        i_mid = value.index(middle)
        
        sL, sC, sR = "", value, ""
        
        if src_pattern.startswith(cls.before):
            if middle: sL = value[:i_mid]
        
        if src_pattern.endswith(cls.after):
            if middle: sR = value[i_mid+len(middle):]
        
        return pattern.replace(cls.before, sL).replace(cls.after, sR).replace(cls.whole, sC)
    
    @classmethod
    def apply_to_attr(cls, obj, attr_name, pattern, src_pattern):
        setattr(obj, attr_name, cls.apply(getattr(obj, attr_name), src_pattern, pattern))
