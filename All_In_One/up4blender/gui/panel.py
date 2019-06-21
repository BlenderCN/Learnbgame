import bpy

bl_info = {
    "name": "Universal Pipeline Blender Adapter",
    "category": "Learnbgame",
}


class UnipipeComponentManagerPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Unipipe Component Management"
    bl_idname = "SCENE_PT_layout"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):

        layout = self.layout
        col = layout.column()

        col.label(text='Publish Resource')
        col.operator("wm.unipipe_publish_resource", text='Publish Resource')
        col.operator("wm.unipipe_update_model_resource", text='Update UVs/Republish Model')

        col.label(text='Import Published Resource')
        row = col.row()
        row.operator("wm.unipipe_append_published_model", text='Import Model')
        row.operator("wm.unipipe_append_published_material", text='Import Material')

        col.operator("wm.unipipe_build_final", text='Build Final')

        col.label(text='Link Published Resource')
        col.operator("wm.unipipe_link_published_final", text='Link Component Resource')
        col.operator("wm.unipipe_link_published_collection", text='Link Context Resource')

        col.label(text='Narrative')
        col.operator("wm.unipipe_set_render_path")
        col.operator("wm.unipipe_set_render_settings")


def register():
    bpy.utils.register_class(UnipipeComponentManagerPanel)


def unregister():
    bpy.utils.unregister_class(UnipipeComponentManagerPanel)
