import bpy
import bpy.utils.previews

import os

preview_collections = {}

class UseCurrentTexture(bpy.types.Operator):
    bl_idname = "material.use_current_texture"
    bl_label = "Add Texture Node"
    bl_options = {'UNDO'}

    def execute(self, context):
        append_texture_node_group(self, context)
        return {'FINISHED'}

class PBRTexturePanel(bpy.types.Panel):
    bl_label = "PBR Texture Nodes"
    bl_idname = "pbr_previews_texture"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    
    @classmethod
    def poll(cls, context):
        if bpy.context.object.active_material:
            return context.scene.render.engine == 'CYCLES' and bpy.context.space_data.tree_type == 'ShaderNodeTree' and bpy.context.space_data.shader_type == 'OBJECT' and bpy.context.object.active_material.use_nodes

    def draw(self, context):
        settings = context.scene.pbr_material_settings
        layout = self.layout
        col = layout.column(align=True)
        
        # Preview
        row = col.row()
        row.template_icon_view(context.scene, "thumbs_tex", show_labels=True)
       
        row = col.row()
        row.operator('material.use_current_texture')

def append_texture_node_group(self, context):
    path = os.path.join(os.path.dirname(__file__), "blends" + os.sep + "textures.blend")
    
    with bpy.data.libraries.load(path, False) as (data_from, data_to):
        node_group = context.scene.thumbs_tex
        if not node_group in bpy.data.node_groups:
            data_to.node_groups = [node_group]
    
    active_material = bpy.context.object.active_material
    
    # Now add the node
    bpy.ops.node.select_all(action='DESELECT')
    
    group = bpy.data.materials[active_material.name].node_tree.nodes.new("ShaderNodeGroup")
    group.node_tree = bpy.data.node_groups[node_group]
    group.location = bpy.context.space_data.edit_tree.view_center
    
def generate_previews():
    previews = preview_collections["pbr_textures"]
    image_location = previews.images_location
    
    enum_items = []
    
    # Generate the thumbnails
    for i, image in enumerate(os.listdir(image_location)):
        filepath = os.path.join(image_location, image)
        thumb = previews.load(filepath, filepath, 'IMAGE')
        enum_items.append((image, image, "", thumb.icon_id, i))
    
    return enum_items

def register():
    previews_tex = bpy.utils.previews.new()
    previews_tex.images_location = os.path.join(os.path.dirname(__file__), "thumbs" + os.sep + 't')
    
    preview_collections['pbr_textures'] = previews_tex

    bpy.types.Scene.thumbs_tex = bpy.props.EnumProperty(
        items=generate_previews(),
        description="Choose the texture you want to use",
        update=append_texture_node_group
    )
    
def unregister():
    for preview in preview_collections.values():
        bpy.utils.previews.remove(preview)
    preview_collections.clear()
    
    del bpy.types.Scene.thumbs_tex