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
    'name': 'Automatic Rig Layer Panel',
    'author': 'Beorn Leonard',
    'version': (0, 5),
    "blender": (2, 66, 0),
    "api": 36157,
    'location': 'View3D > Properties panel > Animation Tools',
    'description': 'Automatically draws a UI panel for switching rig layers.',
    "wiki_url": "",
    "tracker_url": "",
    'category': 'Animation'}

"""
This script draws a layer switching panel for your rig. It will automatically work with any rig which is set up to call it.

To set up your rig:
1) Make a property called "autoRigLayers" and set its value to "1"
2) Make a property called "layer.1" and set its value to whatever label you want for layer 1's button.
3) Repeat step 2 for all the rig layers that you want to appear on the panel

Optionally you can add set the number of columns in the panel.
This is done by adding property called "layer.cols" and setting its value to a whole number.
"""

import bpy

class LayerPanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Rig Layers"

    @classmethod
    def poll(self, context):
        try:
            return (bpy.context.active_object.data.get("autoRigLayers"))
        except (AttributeError, KeyError, TypeError):
            return False

    def draw(self, context):
        layout = self.layout
        obj = context.object

        # get layer names
        layers = []
        y = -1
        for x in range (1, 32):
            layerNum = "layer." + str(x)
            if (bpy.context.active_object.data.get(layerNum)):
                y+=1
                layers.append([])
                layerName = bpy.context.active_object.data.get(layerNum)
                layers[y].append(x)
                layers[y].append(layerName)

        # draw layer buttons
        if (bpy.context.active_object.data.get("layer.cols")):
            layer_cols = int(bpy.context.active_object.data.get("layer.cols"))
            row = layout.row()
        else:
            layer_cols = 1

        for x in range (len(layers)):
           if (x%layer_cols  == 0):
               row = layout.row()
           row.prop(context.active_object.data, 'layers', index=(layers[x][0]-1), toggle=True, text=layers[x][1], icon='VISIBLE_IPO_ON')


def register():
    bpy.utils.register_class(LayerPanel)

def unregister():
    bpy.utils.unregister_class(LayerPanel)

