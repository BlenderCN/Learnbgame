import bpy

debugMode = False

class LayoutDemoPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Texture CSV Panel"
    bl_idname = "SCENE_PT_layout"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        global debugMode

        layout = self.layout
        scene = context.scene

        row = layout.row()
        wm = bpy.context.window_manager
        row.prop(wm, "csv_dir")

        row = layout.row()
        row.operator("images.path_change_extension")
        #row.operator("images.path_export_csv_old")
        row = layout.row()
        row.operator("images.path_export_csv", text = "New CSV").my_append = False
        row.operator("images.path_export_csv", text = "Append To CSV").my_append = True

        row = layout.row()
        row.operator("images.load_from_csv")


        row = layout.row()
        row.label("Create Material Tree")
        row = layout.row()
        row.prop(wm, "texture_dir")
        row = layout.row()
        row.operator("images.create_nodetree")

        #row = layout.row()
        #


        if debugMode == True:
            row = layout.row()
            row.label(text = "Debut Mode")
            row.operator("images.path_print_import_csv")
            row.operator("images.load_from_csv_replace001")
            row.operator("images.images.path_print_csv")
            row.operator("images.find_in_csv")


