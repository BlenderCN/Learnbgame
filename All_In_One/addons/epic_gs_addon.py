bl_info = {
    "name" : "EPIC GS data Processor",
    "author" : "David C. King",
    "version" : (2, 79, 0),
    "location" : "View3D > Tools > Create",
    "description" : "Process EPIC.GS data files into full animations: 1 object per cell",
    "tracker_url" : "https://github.com/meekrob/c-blenderi/issues",
    "warning" : "",
    "wiki_url" : "https://github.com/meekrob/c-blenderi/wiki",
    "category": "Learnbgame",
}

import bpy
from bpy.props import StringProperty
from bpy.props import CollectionProperty
import sys

class OBJECT_OT_epic(bpy.types.Operator):
    """Epic processing button"""
    bl_label = "Process file"
    bl_idname = "object.epic"
    bl_options = {'REGISTER'}

    run_this_shit = False

    def execute(self, context):
        print("Running this shit: FILEPATH %s" % context.scene.epic_gs_filename)
        if context.scene.epic_gs_filename == '':
            self.report({'ERROR_INVALID_INPUT'}, "Need to specify a file")
            return {'CANCELLED'}

        self.report({'INFO'}, "Processing file: %s" % context.scene.epic_gs_filename)
        return {'FINISHED'}

        

class OBJECT_OT_custompath(bpy.types.Operator):
    #bl_label = "Select epic.gs data file"
    bl_label = "Process EPIC.GS file"
    bl_idname = "object.custom_path"
    __doc__ = ""

    bl_options = {'REGISTER'}

    filename_ext = "*.csv"
    filter_glob = StringProperty(
        name = "Filename",
        description = "File to Process",
        default=filename_ext, options={'HIDDEN'}
    )    

    filepath = StringProperty(
        name="File Path", 
        description="Filepath used for importing txt files", 
        maxlen= 1024, 
        default= "")

    def execute(self, context):
        print("FILEPATH %s"%self.properties.filepath)#display the file name and current path        
        context.scene.epic_gs_filename = self.properties.filepath
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class file_processing_panel(bpy.types.Panel):
    """File processing panel"""
    bl_label = "Epic.gs.data processer"
    bl_idname = "OBJECT_PT_file_process"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Create"
    bl_context = "objectmode"

    def draw(self, context):
        #obj = bpy.context.scene.objects.get("embryo_parent")
        scene = bpy.context.scene

        layout = self.layout
        row = layout.row()
        row.label(text="Open and process an epic.gs.data file:")
        row = layout.row(align=True)
        row.prop( context.scene, "epic_gs_filename", text="")
        p = row.operator( OBJECT_OT_custompath.bl_idname, text="", icon = "FILESEL")
        p.filepath = context.scene.epic_gs_filename 

        row = layout.row()
        row.label(text="Setup:")

        # empty parent for everything
        row = layout.row()
        row.label(text="Embryo parent")
        row.prop_search(scene, "embryo_parent", scene, "objects", text="")

        # cell type object templates
        row = layout.row()
        row.label(text="Object templates for cell types:")

        row = layout.row()
        split = row.split()

        col = split.column()
        col.label(text="C cell:")
        col.prop_search(scene, "C_cell_template", scene, "objects", text="")

        col = split.column()
        col.label(text="D cell:")
        col.prop_search(scene, "D_cell_template", scene, "objects", text="")

        row = layout.row()
        split = row.split()

        col = split.column()
        col.label(text="E cell:")
        col.prop_search(scene, "E_cell_template", scene, "objects", text="")

        col = split.column()
        col.label(text="P cell:")
        col.prop_search(scene, "P_cell_template", scene, "objects", text="")

        row = layout.row()
        row.label(text="Operations:")
        row = layout.row()
        p = row.operator(OBJECT_OT_epic.bl_idname)
        


def process_epic_gs_button(self, context):
    self.layout.operator('file.select_all_toggle',        
        OBJECT_OT_custompath.bl_idname,
        icon = "FILESEL"
    )

def layers_tuple(selected=0):
    layer_list = [False] * 20
    layer_list[0] = True
    return tuple(layer_list)


# registration
def register():
    print("-register-", file=sys.stderr)

    """
    # While trying to activate as an add-on
    # AttributeError: '_RestrictContext' object has no attribute 'scene'
    if bpy.context.scene.objects.find("embryo_parent") < 0:
        bpy.ops.object.empty_add(
            type='PLAIN_AXES', 
            view_align=False, 
            location=(0, 0, 0), 
            layers=layers_tuple()
        )
        bpy.context.object.name = "embryo_parent"
    """

    bpy.types.Scene.epic_gs_filename = bpy.props.StringProperty(
        name = "Epic filename",
        default = "",
        description = "Epic gs name"
    )
    main_blender_object = bpy.types.Scene
    #blender_object = bpy.types.Object
    main_blender_object.embryo_parent = bpy.props.StringProperty(
        name = "Embryo object parent",
        default = "embryo_parent",
        description = "All added objects are parented to this object"
    )

    main_blender_object.C_cell_template = bpy.props.StringProperty(
        name = "C Cell Object template",
        default = "",
        description = "This object will be cloned to produce all of the C cells in the data file"
    )
    main_blender_object.D_cell_template = bpy.props.StringProperty(
        name = "D Cell Object template",
        description = "This object will be cloned to produce all of the D cells in the data file"
    )
    main_blender_object.E_cell_template = bpy.props.StringProperty(
        name = "E Cell Object template",
        description = "This object will be cloned to produce all of the E cells in the data file"
    )
    main_blender_object.P_cell_template = bpy.props.StringProperty(
        name = "P Cell Object template",
        description = "This object will be cloned to produce all of the P cells in the data file"
    )


    bpy.utils.register_class(OBJECT_OT_epic)
    bpy.utils.register_class(OBJECT_OT_custompath)
    bpy.utils.register_class(file_processing_panel)
    bpy.types.INFO_MT_mesh_add.append(process_epic_gs_button)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_epic)
    bpy.utils.unregister_class(OBJECT_OT_add_custompath)
    bpy.utils.unregister_class(file_processing_panel)
    bpy.types.INFO_MT_mesh_add.remove(process_epic_gs_button)

if __name__ == "__main__":
    register()
