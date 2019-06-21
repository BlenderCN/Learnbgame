import bpy
import bpy.utils.previews

import os

preview_collections = {}

class UseCurrentMaterial(bpy.types.Operator):
    bl_idname = "material.use_current_material_node"
    bl_label = "Add Material Node"
    bl_options = {'UNDO'}

    def execute(self, context):
        append_material_node(self, context)
        return {'FINISHED'}
        

class PBRMaterialPanelNode(bpy.types.Panel):
    bl_label = "PBR Material Nodes"
    bl_idname = "pbr_previews_node"
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
        
        row = col.row()
        row.prop(settings, 'category_node', text="Category", expand=True)
        
        # Preview
        row = col.row()
        if settings.category_node == 'm':
            row.template_icon_view(context.scene, "thumbs_mats_metals_node", show_labels=True)
        elif settings.category_node == 'd':
            row.template_icon_view(context.scene, "thumbs_mats_dielectrics_node", show_labels=True)
       
        row = col.row()
        row.operator('material.use_current_material_node')
        

def generate_previews(metals):
    if metals:
        previews = preview_collections["pbr_materials_metals_node"]
    else:
        previews = preview_collections["pbr_materials_dielectrics_node"]
    image_location = previews.images_location
    
    enum_items = []
    
    # Generate the thumbnails
    for i, image in enumerate(os.listdir(image_location)):
        filepath = os.path.join(image_location, image)
        thumb = previews.load(filepath, filepath, 'IMAGE')
        
        enum_items.append((image, image, "", thumb.icon_id, i))
    return enum_items
    
def append_material_node(self, context):
    settings = context.scene.pbr_material_settings

    if settings.category_node == 'm':
        path = os.path.join(os.path.dirname(__file__), "blends" + os.sep + "metals.blend")
    elif settings.category_node == 'd':
        path = os.path.join(os.path.dirname(__file__), "blends" + os.sep + "dielectrics.blend")
    
    with bpy.data.libraries.load(path, False) as (data_from, data_to):       
        if settings.category_node == 'm':
            mat_name = context.scene.thumbs_mats_metals_node
        elif settings.category_node == 'd':
            mat_name = context.scene.thumbs_mats_dielectrics_node

        if not mat_name in bpy.data.node_groups:
            data_to.node_groups = [mat_name]
    
    active_material = bpy.context.object.active_material
    
    # Now add the node
    bpy.ops.node.select_all(action='DESELECT')
    
    group = bpy.data.materials[active_material.name].node_tree.nodes.new("ShaderNodeGroup")
    group.node_tree = bpy.data.node_groups[mat_name]
    group.location = bpy.context.space_data.edit_tree.view_center

def register():
    previews_mat_metals = bpy.utils.previews.new()
    previews_mat_metals.images_location = os.path.join(os.path.dirname(__file__), "thumbs" + os.sep + 'm')
    
    previews_mat_dielectrics = bpy.utils.previews.new()
    previews_mat_dielectrics.images_location = os.path.join(os.path.dirname(__file__), "thumbs" + os.sep + 'd')

    preview_collections['pbr_materials_metals_node'] = previews_mat_metals
    preview_collections['pbr_materials_dielectrics_node'] = previews_mat_dielectrics
    
    bpy.types.Scene.thumbs_mats_metals_node = bpy.props.EnumProperty(
        items=generate_previews(True),
        description="Choose the material you want to use",
        update=append_material_node,
        default='Gold'
    )
    bpy.types.Scene.thumbs_mats_dielectrics_node = bpy.props.EnumProperty(
        items=generate_previews(False),
        description="Choose the material you want to use",
        update=append_material_node,
        default='Plastic'
    )
    
def unregister():
    for preview in preview_collections.values():
        bpy.utils.previews.remove(preview)
    preview_collections.clear()
    
    del bpy.types.Scene.thumbs_mats_metals_node
    del bpy.types.Scene.thumbs_mats_dielectrics_node