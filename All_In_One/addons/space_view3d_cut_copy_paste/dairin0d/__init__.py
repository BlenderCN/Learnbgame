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

"""
Utility modules by dairin0d
"""

#__all__ = ("module1", "module2", etc.) # in case we want to not export something

"""
# !!! This is the new correct way (the imp module is considered obsolete)
if "bpy" in locals():
    import importlib
    if "import_obj" in locals():
        importlib.reload(import_obj)
    if "export_obj" in locals():
        importlib.reload(export_obj)
"""

if "_reload" in locals(): _reload(locals())

try:
    from . import version
    from . import utils_python
    from . import utils_math
    from . import utils_text
    from . import utils_accumulation
    from . import utils_gl
    from . import utils_ui
    from . import bpy_inspect # uses utils_python, utils_text
    from . import utils_blender # uses bpy_inspect
    from . import utils_userinput # uses utils_python, bpy_inspect
    from . import utils_view3d # uses bpy_inspect, utils_math, utils_ui, utils_gl, utils_blender
    from . import utils_addon # uses utils_python, utils_text, utils_ui, bpy_inspect
except Exception as exc:
    # For some reason errors that happen during dairin0d importing aren't automatically printed
    import traceback
    print()
    traceback.print_exc()
    print()

def _reload(module_locals):
    import imp
    for key, value in tuple(module_locals.items()): # make a copy!
        if key.startswith("_"): continue
        module_locals[key] = imp.reload(value)
    return module_locals # just in case
