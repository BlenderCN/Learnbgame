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
    'name': 'Copy Render Layer',
    'author': 'Bartek Skorupa',
    'version': (0, 7),
    'blender': (2, 7, 0),
    'location': "Render Layers Panel",
    'description': 'Copy, Paste or Duplicate Render Layer',
    "category": "Learnbgame",
    "warning": "When pasting render layer to different file double check material and light override",
    'wiki_url': "http://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/Render/Copy_Render_Layer",
    'tracker_url': "http://projects.blender.org/tracker/index.php?func=detail&aid=34109&group_id=153&atid=467",
    }

import bpy
from bpy.props import StringProperty

# excludes: Attributes of render layer that will not be taken into account.
excludes = ('__doc__', '__module__', '__slots__', 'bl_rna', 'rna_type', 'freestyle_settings')

# layers_sets:
# 'layers_exclude', 'layers_zmask' and 'layers' attributes need special handling when pasted to different file.
# When analyzed attribute is one of them - data will be stored in layers_sets_values list
layers_sets = ('layers_exclude', 'layers_zmask', 'layers')

# overrides:
# 'light_override' and 'material_override' attributes need special handling when pasted to different file
# When analyzed attribute is one of them - names of material or light group will be stored in:
# copied_material_override and copied_light_override
overrides = ('light_override', 'material_override')


class RENDER_OT_copy_render_layer(bpy.types.Operator):
    bl_idname = "render.copy_render_layer"
    bl_label = "Copy/Paste/Duplicate Render Layer"
    
    # option: (will be set when calling operator)
    # Available options: 'Duplicate', 'Copy', 'Copy All', 'Paste'
    option = StringProperty()
    
    # copied_data: (will be set suring execution with options 'Copy' or 'Copy All')
    # String from list of entries for every copied render layer.
    # entry: [copied_attributes, copied_layers_sets, material_override, light_override]
    # 
    # copied_attributes:
    # [[attr, value], [attr2, value2], (...) ]
    # 
    # copied_layers_sets: list of 3 boolean lists for 'layers_exclude', 'layers_zmask', 'layers'
    # each boolean list contains 20 booleans representing individual layers (is or is not active).
    # 
    # copied_material_override - Name of material used as material override.
    # 
    # copied_light_override: Name of light group used as light override.
    copied_data = StringProperty()
    
    @classmethod
    def poll(cls, context):
        return context.scene.render.layers.active
    
    def execute(self, context):
        layers = context.scene.render.layers
        rl = layers.active
        display_warning = False
        
        if self.option == 'Duplicate':
            bpy.ops.scene.render_layer_add()
            rl_copy = layers.active
            for attr in (a for a in dir(rl) if a not in excludes):
                setattr(rl_copy, attr, getattr(rl, attr))
        
        elif self.option == 'Copy' or self.option == 'Copy All':
            all_attributes = []
            if self.option == 'Copy':
                layers = [rl]
            for rl in layers:
                attributes_list = []
                layers_sets_values = []
                material_override_name = ''
                light_override_name = ''
                for attr in (
                        a for a in dir(rl) if
                        a not in excludes and
                        a not in layers_sets and
                        a not in overrides
                        ):
                    attributes_list.append([attr, getattr(rl, attr)])
                if rl.material_override:
                    material_override_name = rl.material_override.name
                if rl.light_override:
                    light_override_name = rl.light_override.name
                for layers_set in layers_sets:
                    layers_set_values = []
                    for layer in range(0, 20):
                        layers_set_values.append(getattr(rl, layers_set)[layer])
                    layers_sets_values.append(layers_set_values)
                all_attributes.append([
                    attributes_list,
                    layers_sets_values,
                    material_override_name,
                    light_override_name
                    ])
            self.copied_data = str(all_attributes)
        
        elif self.option == 'Paste':
            if self.copied_data:  # If 'Copy' hasn't been executed earlier - self.copied_data is empty.
                copied_data = eval(self.copied_data)
                for [
                    copied_attributes,
                    copied_layers_sets_values,
                    copied_material_override,
                    copied_light_override
                    ] in copied_data:
                        bpy.ops.scene.render_layer_add()
                        rl_copy = layers.active
                        for [attr, attr_value] in copied_attributes:
                            setattr(rl_copy, attr, attr_value)
                        for layers_set in layers_sets:
                            for l in range(0, 20):
                                if layers_set == 'layers_exclude':
                                    rl_copy.layers_exclude[l] = copied_layers_sets_values[0][l]
                                elif layers_set == 'layers_zmask':
                                    rl_copy.layers_zmask[l] = copied_layers_sets_values[1][l]
                                elif layers_set == 'layers':
                                    rl_copy.layers[l] = copied_layers_sets_values[2][l]
                        if copied_material_override:
                            mat = [m for m in bpy.data.materials if m.name == copied_material_override]
                            if mat:
                                rl_copy.material_override = mat[0]
                            else:
                                display_warning = True
                        if copied_light_override:
                            group = [g for g in bpy.data.groups if g.name == copied_light_override]
                            if group:
                                rl_copy.light_override = group[0]
                            else:
                                display_warning = True
        if display_warning:
            self.report({'INFO'}, "Some material or light override failed")
        
        return {'FINISHED'}

def buttons(self, context):
    layout = self.layout
    row = layout.row(align=True)
    row.operator(
        RENDER_OT_copy_render_layer.bl_idname,
        emboss=True,
        text="Duplicate",
        icon="GHOST",
        ).option = 'Duplicate'
    row.operator(
        RENDER_OT_copy_render_layer.bl_idname,
        emboss=True,
        text="Copy",
        icon="COPYDOWN",
        ).option = 'Copy'
    row.operator(
        RENDER_OT_copy_render_layer.bl_idname,
        emboss=True, text="Copy All",
        icon="COPYDOWN",
        ).option = 'Copy All'
    row.operator(
        RENDER_OT_copy_render_layer.bl_idname,
        emboss=True,
        text="Paste",
        icon="PASTEDOWN",
        ).option = 'Paste'
    
def register():
    bpy.utils.register_module(__name__)
    bpy.types.RENDERLAYER_PT_layers.prepend(buttons)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.RENDERLAYER_PT_layers.remove(buttons)

if __name__ == "__main__":
    register()
