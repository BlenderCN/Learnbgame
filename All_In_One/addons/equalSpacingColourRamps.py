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


bl_info = {
    "name": "Evenly Space ColourRamp Node Handles",
    "description": "Evenly space ColourRamp node handles.",
    "author": "Ray Mairlot",
    "version": (1, 0),
    "blender": (2, 71, 0),
    "location": "Node Editor > Q over selected ColourRamp node",
    "category": "Learnbgame"
}
    

import bpy
    

class equaliseColourRampOperator(bpy.types.Operator):
    """ Evenly space ColourRamp handles for the selected colour ramp node """
    bl_idname = "node.even_colour_ramp"
    bl_label = "Evenly space ColourRamp node handles"


    def execute(self, context):
        main(context)
        return {'FINISHED'}


def main(context):
    if context.active_node:  
        if context.active_node.type == "VALTORGB":                          
            handles = context.active_node.color_ramp.elements
            if len(handles)>1:

                increment = 1/(len(handles)-1)
                position = 0

                for handle in handles:
                    handle.position = position
                    position+=increment


def register():
    bpy.utils.register_class(equaliseColourRampOperator)

    kc = bpy.context.window_manager.keyconfigs.addon

    km = kc.keymaps.new(name='Node Editor', space_type='NODE_EDITOR')
    km.keymap_items.new("node.even_colour_ramp", 'Q', 'PRESS')



def unregister():
    bpy.utils.unregister_class(equaliseColourRampOperator)
    
    kc = bpy.context.window_manager.keyconfigs.addon
    kc.keymaps.remove(kc.keymaps['Node Editor'])
    


if __name__ == "__main__":
    register()



