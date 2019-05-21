# --------------------------------------------------------------------------
# BlenderAndMBDyn
# Copyright (C) 2015 G. Douglas Baldwin - http://www.baldwintechnology.com
# --------------------------------------------------------------------------
# ***** BEGIN GPL LICENSE BLOCK *****
#
#    This file is part of BlenderAndMBDyn.
#
#    BlenderAndMBDyn is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    BlenderAndMBDyn is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with BlenderAndMBDyn.  If not, see <http://www.gnu.org/licenses/>.
#
# ***** END GPL LICENCE BLOCK *****
# -------------------------------------------------------------------------- 

from .common import Tree

collision_tree = Tree([
    ("Collision world", None),
    ("Box", 2),
    ("Capsule", 2),
    ("Cone", 2),
    ("Plane", 2),
    ("Sphere", 2)])

# Each module
tree = Tree([
    ("Module load", None),
    ("Sandbox", 2),
    ("Collision", collision_tree)])

# Types in this list will become MBDyn elements, in order
loadable_element_types = [
    "Sandbox",
    "Box",
    "Capsule",
    "Cone",
    "Plane",
    "Sphere",
    "Collision world"]

# Types in these lists will become MBDyn nodes
structural_static_types = []

structural_dynamic_types = []

# Types in this list will be be handled like a Rigid offset
offset_types = ["Box", "Cone", "Capsule", "Plane", "Sphere"]
