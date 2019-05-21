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

# Material Helper UI
# By Matti 'Menithal' Lahtinen

import bpy

from bpy.props import (
    StringProperty,
    BoolProperty,
    FloatVectorProperty,
    FloatProperty
)


def update_color(self, context):
    mat = context.material
    mat.diffuse_color = mat.hifi_material_color

    
def update_roughness(self, context):
    mat = context.material
    # Hifi values are inverse as Blender Hardness actually defines Glossiness.
    mat.specular_hardness = int((1-(mat.hifi_roughness_float / 100))*512)


def update_metallicness(self, context):
    mat = context.material
    per = mat.hifi_metallic_float/100
    mat.specular_color = (per, per, per)
    

def update_transparency(self, context):
    mat = context.material
    mat.alpha = 1 - mat.hifi_transparency_float/100
    if mat.alpha < 1:
        mat.use_transparency = True
        mat.transparency_method = 'Z_TRANSPARENCY'        
    else:
        mat.use_transparency = False

# Helper functions to make code a bit more readable, and using less large functions that do the same thing
def that_has_diffuse (texture_slot): return texture_slot.use_map_color_diffuse

def that_has_transparency ( texture_slot): return texture_slot.use_map_alpha

def that_has_emit ( texture_slot): return texture_slot.use_map_emit

def that_has_metallicness (texture_slot): return texture_slot.use_map_color_spec

def that_has_glossiness ( texture_slot): return texture_slot.use_map_hardness

def that_has_normal (texture_slot): return texture_slot.use_map_normal

# Various operations used as short hands

def texture_operation_diffuse( slot, mode, texture):
    slot.use_map_color_diffuse = mode
    
        
def texture_operation_glossiness( slot, mode, texture ):
    slot.use_map_hardness = mode
    
    
def texture_operation_metallic( slot, mode, texture ):
    slot.use_map_color_spec = mode
    

def texture_operation_normal (slot, mode, texture ):
    slot.use_map_normal = mode
    texture.use_normal_map = mode
    

def texture_operation_transparency( slot, mode,  texture):
    slot.use_map_alpha = mode
    
    
def texture_operation_emit( slot, mode,texture):
    slot.use_map_emit = mode
    

# find first texture in material that has *
# Takes a material context, and uses has_operation function to search for something
def find_first_texture_in(has_operation):
    current_textures = bpy.context.active_object.active_material.texture_slots
    
    found_slot = None
    for texture_slot in current_textures: 
        if texture_slot is not None:
            
            result = has_operation(texture_slot)
            if result:
                found_slot = texture_slot                           
                break
    
    return found_slot


class HifiMaterialOperator(bpy.types.Panel):
    bl_idname = "material_helper.hifi"
    bl_label = "High Fidelity Material Helper"
    
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"
    
    COMPAT_ENGINES = {'BLENDER_RENDER'}
    
    bpy.types.Material.hifi_material_color = FloatVectorProperty(
        name = "Tint",
        description = "Set Material Tint",
        default = (0.8, 0.8, 0.8),
        min = 0.0,
        max = 1.0,
        subtype = "COLOR",
        update = update_color
    )
        
    bpy.types.Material.hifi_roughness_float = FloatProperty(
        name = "Roughness",
        description = "Set Roughness",
        default = 30,
        min = 0.0,
        max = 100,
        subtype = "PERCENTAGE",
        update = update_roughness
    )

    bpy.types.Material.hifi_metallic_float = FloatProperty(
        name = "Metallicness",
        description = "Set Metallicness",
        default = 0.0,
        min = 0.0,
        max = 100,
        subtype = "PERCENTAGE",
        update = update_metallicness
    )

    bpy.types.Material.hifi_transparency_float = FloatProperty(
        name = "Transparency",
        description = "Set Transparency",
        default = 0.0,
        min = 0.0,
        max = 100,
        subtype = "PERCENTAGE",
        update = update_transparency
    )
    
    
    @classmethod
    def poll(self, context):
        mat = context.material
        engine = context.scene.render.engine
        return mat and engine in self.COMPAT_ENGINES
    
        
    def draw (self, context):
        layout = self.layout
        
        row = layout.row()
        
        row.prop(context.material, "hifi_material_color")             
        row.operator(HifiResetDiffuseOperator.bl_idname)
                
        build_texture_ui(context, layout, HifiDiffuseTextureOperator)
        build_texture_ui(context, layout, HifiRoughnessTextureOperator, "hifi_roughness_float")
        
        layout.label(text='Note, Glossiness is inverse of Roughness')
        layout.separator()
        
        build_texture_ui(context, layout, HifiMetallicTextureOperator, "hifi_metallic_float")
        build_texture_ui(context, layout, HifiNormalTextureOperator)
        build_texture_ui(context, layout, HifiTransparencyTextureOperator, "hifi_transparency_float")
        
        build_texture_ui(context, layout, HifiEmitTextureOperator)
        
 
       # setattr(mat, "hifi_material_color", mat.diffuse_color)
       # mat.specular_hardness = int((1-(mat.hifi_roughness_float / 100))*512)
       # setattr(mat, "hifi_roughness_float", (1 - mat.specular_hardness / 512) * 100)
       # setattr(mat, "hifi_metallic_float", mat.specular_color[0] * 100)
       # setattr(mat, "hifi_transparency_float")
                    

def build_texture_ui(context, layout, operator, float_widget = None):
    material = context.material
    texture_slot = find_first_texture_in(lambda slot: operator.has_operation(None, slot))
     
    if texture_slot and texture_slot.texture.type != 'NONE':
        layout.label(text = operator.bl_label)
        split = layout.split(0.9)
        box = split.box()
        
        # TODO: allow previews, but tried it and was having issues:

        #box.template_preview(texture_slot.texture, 
        #    parent=material, slot=texture_slot, 
        #    preview_id=operator.bl_label+'preview')
        
        box.template_image(texture_slot.texture, "image", texture_slot.texture.image_user)
        
        button = split.operator(operator.bl_idname, icon='X', text="")
        button.enabled = False
 
    else:
        row = layout.row()
        
        if float_widget:
            row.prop(material, float_widget)            
                
        button = row.operator(operator.bl_idname, icon='ZOOMIN')
        button.enabled = True
        
    layout.separator()
    
    

class HifiResetDiffuseOperator(bpy.types.Operator):
    bl_idname = HifiMaterialOperator.bl_idname + "_diffuse_reset_color"
    bl_label = "Reset Tint" 
   
    def execute(self, context):
        mat = context.material
        mat.hifi_material_color = (1,1,1)
        mat.diffuse_color = (1,1,1)
        layout = self.layout
        
        return {'FINISHED'} 
      
    
class HifiGenericTextureOperator(bpy.types.Operator):

    bl_idname = HifiMaterialOperator.bl_idname + "_generic_reset_color"
    bl_label = "Reset Tint" 
   
    has_operation = None
    texture_operation = None
    postfix = ""
    enabled = True
    
    def execute(self, context):
        if self.texture_operation is not None and self.has_operation is not None:
     
            found_slot = find_first_texture_in(self.has_operation)
            print("Found Slot", found_slot, self.enabled)
            if self.enabled and found_slot is None:
            
                material = bpy.context.active_object.active_material
                slots = material.texture_slots
                name = material.name + "_" + self.postfix
                texture = bpy.data.textures.new(name, 'IMAGE')
                slot = slots.add()
                slot.use_map_color_diffuse = False
                self.texture_operation(slot, True, texture)
                slot.texture = texture
            elif not self.enabled and found_slot:
                self.texture_operation(found_slot, False, None)
                found_slot.use = False
                
        return {'FINISHED'}
        
    

class HifiDiffuseTextureOperator(HifiGenericTextureOperator, bpy.types.Operator):
    bl_idname = HifiMaterialOperator.bl_idname + "_diffuse_texture"
    bl_label = "Diffuse"
    enabled = BoolProperty(name="enabled", default=True)
    
    def has_operation(self, slot): return that_has_diffuse(slot)
    def texture_operation(self, slot, mode, texture): texture_operation_diffuse(slot, mode, texture)

    postfix = "diffuse"
    
    
class HifiRoughnessTextureOperator(HifiGenericTextureOperator, bpy.types.Operator):
    bl_idname = HifiMaterialOperator.bl_idname + "_glossiness_texture"
    bl_label = "Glossiness"
    enabled = BoolProperty(name="enabled", default=True)
    
    def has_operation(self, slot): return that_has_glossiness(slot)
    def texture_operation(self, slot, mode, texture): texture_operation_glossiness(slot, mode, texture)

    postfix = "glossiness"
    
    
class HifiMetallicTextureOperator(HifiGenericTextureOperator, bpy.types.Operator):
    bl_idname = HifiMaterialOperator.bl_idname + "_metallic_texture"
    bl_label = "Metallicness"
    enabled = BoolProperty(name="enabled", default=True)
    
    def has_operation(self, slot): return that_has_metallicness(slot)
    def texture_operation(self, slot, mode, texture): texture_operation_metallic(slot, mode, texture)

    postfix = "metallicness"


class HifiNormalTextureOperator(HifiGenericTextureOperator, bpy.types.Operator):
    bl_idname = HifiMaterialOperator.bl_idname + "_normal_texture"
    bl_label = "Normal"
    enabled = BoolProperty(name="enabled", default=True)
    
    def has_operation(self, slot): return that_has_normal(slot)
    def texture_operation(self, slot, mode, texture): texture_operation_normal(slot, mode, texture)
    
    postfix = "normal"


class HifiTransparencyTextureOperator(HifiGenericTextureOperator, bpy.types.Operator):
    bl_idname = HifiMaterialOperator.bl_idname + "_transparency_texture"
    bl_label = "Transparency"
    enabled = BoolProperty(name="enabled", default=True)
   
    def has_operation(self, slot): return that_has_transparency(slot)
    def texture_operation(self, slot, mode, texture):
        mat = bpy.context.active_object.active_material
        if mode:
            mat.use_transparency = True
            mat.transparency_method = 'Z_TRANSPARENCY'       
        else:
            mat.use_transparency = False      

        texture_operation_transparency(slot, mode, texture)
    
    postfix = "transparency"
    
    
class HifiEmitTextureOperator(HifiGenericTextureOperator, bpy.types.Operator):
    bl_idname = HifiMaterialOperator.bl_idname + "_emit_texture"
    bl_label = "Emit"
    enabled = BoolProperty(name="enabled", default=True)
        
    def has_operation(self, slot): return that_has_emit(slot)
    def texture_operation(self, slot, mode, texture): texture_operation_emit(slot, mode, texture)
    
    postfix = "emit"
    
    
    
classes = [
    HifiResetDiffuseOperator,
    HifiDiffuseTextureOperator,
    HifiRoughnessTextureOperator,
    HifiMetallicTextureOperator,
    HifiNormalTextureOperator,
    HifiTransparencyTextureOperator,
    HifiEmitTextureOperator,
    HifiMaterialOperator
    
]

def register():
    for cls in classes:    
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:    
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()