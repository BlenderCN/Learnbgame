import bpy
import bpy.utils.previews

import os

preview_collections = {}

class UseCurrentMaterial(bpy.types.Operator):
    bl_idname = "material.use_current_material"
    bl_label = "Use Current Material"
    bl_options = {'UNDO'}
    
    def execute(self, context):
        append_material(self, context)
        return {'FINISHED'}

class PBRMaterialPanel(bpy.types.Panel):
    bl_label = "PBR Materials"
    bl_idname = "pbr_previews"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "material"
    
    def draw_header(self, context):
        settings = context.scene.pbr_material_settings
        layout = self.layout
        
        layout.prop(settings, 'enabled', text='')
    
    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'CYCLES'

    def draw(self, context):
        settings = context.scene.pbr_material_settings
        layout = self.layout
        
        layout.enabled = settings.enabled
        
        col = layout.column(align=True)
        
        row = col.row()
        row.prop(settings, 'category', text="Category", expand=True)
        
        # Preview
        row = col.row()
        if settings.category == 'm':
            row.template_icon_view(context.scene, "thumbs_mats_metals", show_labels=True)
        elif settings.category == 'd':
            row.template_icon_view(context.scene, "thumbs_mats_dielectrics", show_labels=True)
       
        row = col.row()
        row.operator('material.use_current_material')
        

def generate_previews(metals):
    if metals:
        previews = preview_collections["pbr_materials_metals"]
    else:
        previews = preview_collections["pbr_materials_dielectrics"]
    image_location = previews.images_location
    
    enum_items = []
    
    # Generate the thumbnails
    for i, image in enumerate(os.listdir(image_location)):
        filepath = os.path.join(image_location, image)
        thumb = previews.load(filepath, filepath, 'IMAGE')
        
        enum_items.append((image, image, "", thumb.icon_id, i))
    return enum_items

def add_nodes(node_name):
    o = bpy.context.active_object 
    
    # If materials exist
    if o.data.materials:
        active_mat = o.active_material
    else:
        active_mat = bpy.data.materials.new(name="Material")
        o.data.materials.append(active_mat)
        
    active_mat.use_nodes = True
    active_mat.node_tree.nodes.clear()
    
    preview_type = active_mat.preview_render_type
    
    # Create nodes
    output = active_mat.node_tree.nodes.new("ShaderNodeOutputMaterial")
    
    group = active_mat.node_tree.nodes.new("ShaderNodeGroup")
    group.node_tree = bpy.data.node_groups[node_name]
    group.location = (-200, 0)
    
    # Link nodes
    active_mat.node_tree.links.new(group.outputs[0], output.inputs[0])
    
    # Hack to refresh the preview
    active_mat.preview_render_type = preview_type
    
def append_material(self, context):
    settings = context.scene.pbr_material_settings

    if settings.category == 'm':
        path = os.path.join(os.path.dirname(__file__), "blends" + os.sep + "metals.blend")
    elif settings.category == 'd':
        path = os.path.join(os.path.dirname(__file__), "blends" + os.sep + "dielectrics.blend")
    
    with bpy.data.libraries.load(path, False) as (data_from, data_to):       
        if settings.category == 'm':
            node_name = context.scene.thumbs_mats_metals
        elif settings.category == 'd':
            node_name = context.scene.thumbs_mats_dielectrics
        
        if not node_name in bpy.data.node_groups:
            data_to.node_groups = [node_name]

    add_nodes(node_name)

def register():
    previews_mat_metals = bpy.utils.previews.new()
    previews_mat_metals.images_location = os.path.join(os.path.dirname(__file__), "thumbs" + os.sep + 'm')
    
    previews_mat_dielectrics = bpy.utils.previews.new()
    previews_mat_dielectrics.images_location = os.path.join(os.path.dirname(__file__), "thumbs" + os.sep + 'd')

    preview_collections['pbr_materials_metals'] = previews_mat_metals
    preview_collections['pbr_materials_dielectrics'] = previews_mat_dielectrics
    
    bpy.types.Scene.thumbs_mats_metals = bpy.props.EnumProperty(
        items=generate_previews(True),
        description="Choose the material you want to use",
        update=append_material,
        default='Gold'
    )
    bpy.types.Scene.thumbs_mats_dielectrics = bpy.props.EnumProperty(
        items=generate_previews(False),
        description="Choose the material you want to use",
        update=append_material,
        default='Plastic'
    )
    
def unregister():
    for preview in preview_collections.values():
        bpy.utils.previews.remove(preview)
    preview_collections.clear()
    
    del bpy.types.Scene.thumbs_mats_metals
    del bpy.types.Scene.thumbs_mats_dielectrics