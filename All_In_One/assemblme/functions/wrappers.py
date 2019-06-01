# Copyright (C) 2019 Christopher Gearhart
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
import time

# Blender imports
import bpy

# Addon imports
from ..functions.common import stopwatch


# https://github.com/CGCookie/retopoflow
def timed_call(label, precision=2):
    def wrapper(fn):
        def wrapped(*args, **kwargs):
            time_beg = time.time()
            ret = fn(*args, **kwargs)
            time_end = time.time()

            time_delta = time_end - time_beg
            stopwatch(label, time_delta, precision=precision)
            return ret
        return wrapped
    return wrapper


# https://github.com/CGCookie/retopoflow
def blender_version(op, ver):
    def nop(*args, **kwargs): pass
    def nop_decorator(fn): return nop
    def fn_decorator(fn): return fn

    major,minor,rev = bpy.app.version
    blenderver = '%d.%02d' % (major,minor)
    # dprint('%s %s %s' % (ver, op, blenderver))
    if   op == '<':  retfn = (blenderver < ver)
    elif op == '<=': retfn = (blenderver <= ver)
    elif op == '==': retfn = (blenderver == ver)
    elif op == '>=': retfn = (blenderver >= ver)
    elif op == '>':  retfn = (blenderver > ver)
    elif op == '!=': retfn = (blenderver != ver)
    else: assert False, 'unhandled op: "%s"' % op
    return fn_decorator if retfn else nop_decorator
