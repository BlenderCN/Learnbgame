"""
PBR Materials Addon
Copyright (C) 2016 Nathan Craddock

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""


bl_info = {
    "name": "PBR Materials",
    "description": "PBR Materials and Procedural Textures",
    "version": (1, 0),
    "blender": (2, 77, 0),
    "author": "Nathan Craddock",
	"wiki_url": "http://wolfflow.weebly.com/materials.html",
    "category": "Material"
}

if "bpy" in locals():
    import importlib
    importlib.reload(materials)
    importlib.reload(textures)
    importlib.reload(material_nodes)
else:
    from . import materials
    from . import textures
    from . import material_nodes
    
import bpy

def addon_toggle(self, context):
    settings = context.scene.pbr_material_settings
    
    if not settings.enabled:
        active_mat = context.active_object.active_material
        
        active_mat.use_nodes = True
        active_mat.node_tree.nodes.clear()
        
        preview_type = active_mat.preview_render_type
        
        # Create nodes
        output = active_mat.node_tree.nodes.new("ShaderNodeOutputMaterial")
        
        diffuse = active_mat.node_tree.nodes.new("ShaderNodeBsdfDiffuse")
        diffuse.location = (-200, 0)
        
        # Link nodes
        active_mat.node_tree.links.new(diffuse.outputs[0], output.inputs[0])
        
        # Hack to refresh the preview
        active_mat.preview_render_type = preview_type

    else:
        materials.append_material(self, context)


# Settings
class PBRMaterialSettings(bpy.types.PropertyGroup):
    category = bpy.props.EnumProperty(
        items=[('m', 'Metals', 'Show metallic materials'),
               ('d', 'Dielectrics', 'Show dielectric materials')],
        description="Choose the category for materials",
        default='d'
    )
    
    category_node = bpy.props.EnumProperty(
        items=[('m', 'Metals', 'Show metallic materials'),
               ('d', 'Dielectrics', 'Show dielectric materials')],
        description="Choose the category for materials",
        default='d'
    )
    
    enabled = bpy.props.BoolProperty(
        name="Enabled",
        description="Use PBR Materials Addon",
        default=False,
        update=addon_toggle
    )
    
def register(): 
    bpy.utils.register_module(__name__)
    materials.register()
    textures.register()
    material_nodes.register()
    
    bpy.types.Scene.pbr_material_settings = bpy.props.PointerProperty(type=PBRMaterialSettings)

def unregister():
    

    bpy.utils.unregister_module(__name__)
    materials.unregister()
    textures.unregister()
    material_nodes.unregister()

    del bpy.types.Scene.pbr_material_settings
