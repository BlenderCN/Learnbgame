# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "Addon",
    "author" : "Hanjo Claassen",
    "description" : "First Addon I wrote",
    "blender" : (2, 80, 0),
    "location" : "View3D",
    "warning" : "",
    "category" : "Generic"
}

import bpy

#######################################
#--------------Operators--------------#
#######################################
from . Array_op     import Test_OT_Operator
from . Array_op     import Array_Path_OperatorOperator
from . Array_op     import Circle_Array_Operator
from . Array_op     import Instance_Collection_Operator
from . Mirror       import Object_MirrorOperator
from . Others       import Update_Scene_Operator


####################################
#--------------Panels--------------#
####################################
from . Panels   import Array
from . Panels   import Mirror
from . Panels   import PIE_Menu
from . Panels    import Others




classes = (
    Test_OT_Operator,
    Circle_Array_Operator,
    Instance_Collection_Operator,
    Object_MirrorOperator,
    Array_Path_OperatorOperator,
    Update_Scene_Operator,

    Array,
    Mirror,
    PIE_Menu,
    Others)
    


addon_keymaps = []

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Window')
    kmi = km.keymap_items.new('wm.call_menu_pie', 'Y', 'PRESS')
    kmi.properties.name = "mesh.pie"
    addon_keymaps.append((km,kmi))

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    
if __name__ == "__main__":
    register()