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

import re

# Already implemented:
# bpy_extras.io_utils.unique_name(key, name, name_dict, name_max=-1, clean_func=None, sep='.')
#def unique_name(src_name, existing_names):
#    name = src_name
#    i = 1
#    while name in existing_names:
#        name = "{}.{:0>3}".format(src_name, i)
#        i += 1
#    return name

# keep_newlines is False by default because Blender doesn't support multi-line tooltips
def compress_whitespace(s, keep_newlines=False):
    #return re.sub("\\s+", " ", s).strip()
    if not keep_newlines: return " ".join(s.split())
    return "\n".join(" ".join(l.split()) for l in s.splitlines())

def indent(s, t):
    res = []
    for l in s.splitlines():
        res.append(t + l)
    return "\n".join(res)

def unindent(s, t=None):
    lines = s.splitlines()
    if t is None:
        nt = len(s)
        for l in lines:
            nd = len(l) - len(l.lstrip())
            # ignore whitespace-only lines
            if nd > 0: nt = min(nt, nd)
    else:
        nt = len(t)
    res = []
    for l in lines:
        nd = len(l) - len(l.lstrip())
        res.append(l[min(nt, nd):])
    return "\n".join(res)

def split_expressions(s, sep="\t", strip=False):
    if sep == "\t":
        text = s
    else:
        sep = sep.strip()
        text = ""
        brackets = 0
        for c in s:
            if c in "[{(":
                brackets += 1
            elif c in "]})":
                brackets -= 1
            if (brackets == 0) and (c == sep):
                c = "\t"
            text += c
    
    res = text.split("\t")
    return ([s.strip() for s in res] if strip else res)

def math_eval(s):
    try:
        return float(eval(s, math.__dict__))
    except Exception:
        # What actual exceptions can be raised by float/math/eval?
        return None

def vector_to_text(v, sep="\t", axes_names="xyzw"):
    sa = []
    for i in range(len(v)):
        s = str(v[i])
        if axes_names:
            s = axes_names[i] + ": " + s
        sa.append(s)
    return sep.join(sa)

def vector_from_text(v, s, sep="\t", axes_names="xyzw"):
    sa = split_expressions(s, sep, True)
    
    if axes_names:
        # first, check if there are keyword arguments
        kw = False
        
        for a in sa:
            if len(a) < 3:
                continue
            
            try:
                # list has no find() method
                i = axes_names.index(a[0].lower())
            except ValueError:
                i = -1
            
            if (i != -1) and (a[1] == ":"):
                v_i = math_eval(a[2:])
                if v_i is not None:
                    v[i] = v_i
                kw = True
        
        if kw:
            return
    
    for i in range(min(len(v), len(sa))):
        v_i = math_eval(sa[i])
        if v_i is not None:
            v[i] = v_i

# From http://www.bogotobogo.com/python/python_longest_common_substring_lcs_algorithm_generalized_suffix_tree.php
# Actually applicable to any sequence with hashable elements
def longest_common_substring(S, T):
    m = len(S)
    n = len(T)
    counter = [[0]*(n+1) for x in range(m+1)]
    longest = 0
    lcs_set = set()
    for i in range(m):
        for j in range(n):
            if S[i] == T[j]:
                c = counter[i][j] + 1
                counter[i+1][j+1] = c
                if c > longest:
                    longest = c
                    lcs_set = {S[i-c+1:i+1]}
                elif c == longest:
                    lcs_set.add(S[i-c+1:i+1])
    return lcs_set
