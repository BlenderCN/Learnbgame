#------------------------------------------------------------------------------
# Reynolds-Blender | The Blender add-on for Reynolds, an OpenFoam toolbox.
#------------------------------------------------------------------------------
# Copyright|
#------------------------------------------------------------------------------
#     Deepak Surti       (dmsurti@gmail.com)
#     Prabhu R           (IIT Bombay, prabhu@aero.iitb.ac.in)
#     Shivasubramanian G (IIT Bombay, sgopalak@iitb.ac.in)
#------------------------------------------------------------------------------
# License
#
#     This file is part of reynolds-blender.
#
#     reynolds-blender is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     reynolds-blender is distributed in the hope that it will be useful, but
#     WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
#     Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with reynolds-blender.  If not, see <http://www.gnu.org/licenses/>.
#------------------------------------------------------------------------------

# -----------
# bpy imports
# -----------
import bpy

# --------------
# python imports
# --------------
import sys, inspect

def get_module_class_members(module_name):
    return [cls_member for cls_member in
            inspect.getmembers(sys.modules[module_name], inspect.isclass)
            if getattr(cls_member[1], '__module__', None) == module_name]

def register_classes(module_name):
    for name, cls_member in get_module_class_members(module_name):
        print('Registering ', name)
        bpy.utils.register_class(cls_member)

def unregister_classes(module_name):
    for name, cls_member in get_module_class_members(module_name):
        print('UnRegistering ', name)
        bpy.utils.unregister_class(cls_member)
