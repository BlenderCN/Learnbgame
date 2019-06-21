"""
Name:    operators
Purpose: Provides operators for importing and exporting and other buttons.

Description:
These operators are used for importing and exporting files, as well as
providing the functions behind the UI buttons.

"""


import bpy
import time
import subprocess

from . import tools
from .common import *
from .layers import *
from .texanim import *

"""
IMPORT AND EXPORT -------------------------------------------------------------
"""

class ImportRV(bpy.types.Operator):
    """
    Import Operator for all file types
    """
    bl_idname = "import_scene.revolt"
    bl_label = "Import Re-Volt Files"
    bl_description = "Import Re-Volt game files"

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        scene = context.scene
        props = scene.revolt
        frmt = get_format(self.filepath)

        start_time = time.time()

        context.window.cursor_set("WAIT")

        print("Importing {}".format(self.filepath))

        if frmt == FORMAT_UNK:
            msg_box("Unsupported format.")

        elif frmt == FORMAT_PRM:
            from . import prm_in
            prm_in.import_file(self.filepath, scene)

            # Enables texture mode after import
            if props.enable_tex_mode:
                enable_any_tex_mode(context)

        elif frmt == FORMAT_CAR:
            from . import parameters_in
            old_check = props.prm_check_parameters
            props.prm_check_parameters = True
            parameters_in.import_file(self.filepath, scene)
            props.prm_check_parameters = old_check
            # Enables texture mode after import
            if props.enable_tex_mode:
                enable_any_tex_mode(context)

        elif frmt == FORMAT_NCP:
            from . import ncp_in
            ncp_in.import_file(self.filepath, scene)

            # Enables texture mode after import
            if props.enable_tex_mode:
                enable_any_tex_mode(context)

        elif frmt == FORMAT_FIN:
            from . import fin_in
            fin_in.import_file(self.filepath, scene)

            # Enables texture mode after import
            if props.enable_tex_mode:
                enable_any_tex_mode(context)

        elif frmt == FORMAT_HUL:
            from . import hul_in
            hul_in.import_file(self.filepath, scene)

            # Enables solid mode after import
            enable_solid_mode()

        elif frmt == FORMAT_TA_CSV:
            from . import ta_csv_in
            ta_csv_in.import_file(self.filepath, scene)

        elif frmt == FORMAT_W:
            from . import w_in
            w_in.import_file(self.filepath, scene)

            # Enables texture mode after import
            if props.enable_tex_mode:
                enable_any_tex_mode(context)


        elif frmt == FORMAT_RIM:
            from . import rim_in
            rim_in.import_file(self.filepath, scene)

        else:
            msg_box("Format not yet supported: {}".format(FORMATS[frmt]))

        end_time = time.time() - start_time

        # Gets any encountered errors
        errors = get_errors()

        # Defines the icon depending on the errors
        if errors == "Successfully completed.":
            ico = "FILE_TICK"
        else:
            ico = "ERROR"

        # Displays a message box with the import results
        msg_box(
            "Import of {} done in {:.3f} seconds.\n{}".format(
                FORMATS[frmt], end_time, errors),
            icon=ico
        )

        context.window.cursor_set("DEFAULT")

        return {"FINISHED"}

    def draw(self, context):
        props = context.scene.revolt
        layout = self.layout
        space = context.space_data

        # Gets the format from the file path
        frmt = get_format(space.params.filename)

        if frmt == -1 and not space.params.filename == "":
            layout.label("Format not supported", icon="ERROR")
        elif frmt != -1:
            layout.label("Import {}:".format(FORMATS[frmt]))

        if frmt in [FORMAT_W, FORMAT_PRM, FORMAT_NCP]:
            box = layout.box()
            box.prop(props, "enable_tex_mode")

        if frmt == FORMAT_W:
            box = layout.box()
            box.prop(props, "w_parent_meshes")
            box.prop(props, "w_import_bound_boxes")
            if props.w_import_bound_boxes:
                box.prop(props, "w_bound_box_layers")
            box.prop(props, "w_import_cubes")
            if props.w_import_cubes:
                box.prop(props, "w_cube_layers")
            box.prop(props, "w_import_big_cubes")
            if props.w_import_big_cubes:
                box.prop(props, "w_big_cube_layers")

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class ExportRV(bpy.types.Operator):
    bl_idname = "export_scene.revolt"
    bl_label = "Export Re-Volt Files"
    bl_description = "Export Re-Volt game files"

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        return exec_export(self.filepath, context)

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def draw(self, context):
        props = context.scene.revolt
        layout = self.layout
        space = context.space_data

        # Gets the format from the file path
        frmt = get_format(space.params.filename)

        if frmt == -1 and not space.params.filename == "":
            layout.label("Format not supported", icon="ERROR")
        elif frmt != -1:
            layout.label("Export {}:".format(FORMATS[frmt]))

        # NCP settings
        if frmt == FORMAT_NCP:
            box = layout.box()
            box.prop(props, "ncp_export_selected")
            box.prop(props, "ncp_export_collgrid")
            box.prop(props, "ncp_collgrid_size")


        # Texture mesh settings
        if frmt in [FORMAT_PRM, FORMAT_W]:
            box = layout.box()
            box.prop(props, "use_tex_num")

        # Mesh settings
        if frmt in [FORMAT_PRM, FORMAT_W]:
            box = layout.box()
            box.prop(props, "apply_scale")
            box.prop(props, "apply_rotation")
        if frmt in [FORMAT_NCP, FORMAT_PRM, FORMAT_W]:
            box = layout.box()
            box.prop(props, "triangulate_ngons")


def exec_export(filepath, context):
    scene = context.scene
    props = context.scene.revolt

    start_time = time.time()
    context.window.cursor_set("WAIT")

    if filepath == "":
        msg_box("File not specified.", "ERROR")
        return {"FINISHED"}

    # Gets the format from the file path
    frmt = get_format(filepath)

    if frmt == FORMAT_UNK:
        msg_box("Not supported for export.", "INFO")
        return {"FINISHED"}
    else:
        # Turns off undo for better performance
        use_global_undo = bpy.context.user_preferences.edit.use_global_undo
        bpy.context.user_preferences.edit.use_global_undo = False

        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode="OBJECT")

        # Saves filepath for re-exporting the same file
        props.last_exported_filepath = filepath

        if frmt == FORMAT_PRM:
            # Checks if a file can be exported
            if not tools.check_for_export(scene.objects.active):
                return {"FINISHED"}

            from . import prm_out
            prm_out.export_file(filepath, scene)

        elif frmt == FORMAT_FIN:
            from . import fin_out
            print("Exporting to .fin...")
            fin_out.export_file(filepath, scene)

        elif frmt == FORMAT_NCP:
            from . import ncp_out
            print("Exporting to .ncp...")
            ncp_out.export_file(filepath, scene)

        elif frmt == FORMAT_HUL:   
            from . import hul_out
            print("Exporting to .hul...")
            hul_out.export_file(filepath, scene)

        elif frmt == FORMAT_W:
            from . import w_out
            print("Exporting to .w...")
            w_out.export_file(filepath, scene)

        elif frmt == FORMAT_RIM:
            from . import rim_out
            print("Exporting to .rim...")
            rim_out.export_file(filepath, scene)

        elif frmt == FORMAT_TA_CSV:
            from . import ta_csv_out
            print("Exporting texture animation sheet...")
            ta_csv_out.export_file(filepath, scene)

        else:
            msg_box("Format not yet supported: {}".format(FORMATS[frmt]))

        # Re-enables undo
        bpy.context.user_preferences.edit.use_global_undo = use_global_undo

    context.window.cursor_set("DEFAULT")

    # Gets any encountered errors
    errors = get_errors()

    # Defines the icon depending on the errors
    if errors == "Successfully completed.":
        ico = "FILE_TICK"
    else:
        ico = "ERROR"

    # Displays a message box with the import results
    end_time = time.time() - start_time
    msg_box(
        "Export to {} done in {:.3f} seconds.\n{}".format(
            FORMATS[frmt], end_time, errors),
        icon=ico
    )

    return {"FINISHED"}


"""
BUTTONS ------------------------------------------------------------------------
"""

class ButtonReExport(bpy.types.Operator):
    bl_idname = "export_scene.revolt_redo"
    bl_label = "Re-Export"
    bl_description = "Redo the same export again"

    def execute(self, context):
        props = context.scene.revolt
        res = exec_export(props.last_exported_filepath, context)
        return res


class ButtonSelectFaceProp(bpy.types.Operator):
    bl_idname = "faceprops.select"
    bl_label = "sel"
    bl_description = "Select or delesect all polygons with this property"
    prop = bpy.props.IntProperty()

    def execute(self, context):
        select_faces(context, self.prop)
        return{"FINISHED"}


class ButtonSelectNCPFaceProp(bpy.types.Operator):
    bl_idname = "ncpfaceprops.select"
    bl_label = "sel"
    bl_description = "Select or delesect all polygons with this property"
    prop = bpy.props.IntProperty()

    def execute(self, context):
        select_ncp_faces(context, self.prop)
        return{"FINISHED"}


class ButtonSelectNCPMaterial(bpy.types.Operator):
    bl_idname = "ncpmaterial.select"
    bl_label = "sel"
    bl_description = "Select all faces of the same material"

    def execute(self, context):
        props = context.scene.revolt
        meshprops = context.object.data.revolt
        props.select_material = meshprops.face_material
        return{"FINISHED"}

"""
VERTEX COLROS -----------------------------------------------------------------
"""

class ButtonColorFromActive(bpy.types.Operator):
    bl_idname = "vertexcolor.copycolor"
    bl_label = "Get Color"
    bl_description = "Gets the color from the active face"

    def execute(self, context):
        color_from_face(context)
        redraw()
        return{"FINISHED"}


class ButtonVertexColorSet(bpy.types.Operator):
    bl_idname = "vertexcolor.set"
    bl_label = "Set Color"
    bl_description = "Apply color to selected faces"
    number = bpy.props.IntProperty()

    def execute(self, context):
        set_vertex_color(context, self.number)
        return{"FINISHED"}


class ButtonVertexColorCreateLayer(bpy.types.Operator):
    bl_idname = "vertexcolor.create_layer"
    bl_label = "Create Vertex Color Layer"
    bl_description = "Creates a vertex color layer"

    def execute(self, context):
        create_color_layer(context)
        return{"FINISHED"}


class ButtonVertexAlphaCreateLayer(bpy.types.Operator):
    bl_idname = "vertexcolor.create_layer_alpha"
    bl_label = "Create Alpha Color Layer"

    def execute(self, context):
        create_alpha_layer(context)
        return{"FINISHED"}



"""
HELPERS -----------------------------------------------------------------------
"""

class ButtonEnableTextureMode(bpy.types.Operator):
    bl_idname = "helpers.enable_texture_mode"
    bl_label = "Enable Texture Mode"
    bl_description = "Enables texture mode so textures can be seen"

    def execute(self, context):
        enable_texture_mode()
        return{"FINISHED"}


class ButtonEnableTexturedSolidMode(bpy.types.Operator):
    bl_idname = "helpers.enable_textured_solid_mode"
    bl_label = "Enable Textured Solid Mode"
    bl_description = "Enables texture mode so textures can be seen"

    def execute(self, context):
        enable_textured_solid_mode()
        return{"FINISHED"}


class ButtonRenameAllObjects(bpy.types.Operator):
    bl_idname = "helpers.rename_all_objects"
    bl_label = "Rename selected"
    bl_description = (
        "Renames all objects for instance export:\n"
        "(example.prm, example.prm.001, ...)"
    )

    def execute(self, context):
        n = tools.rename_all_objects(self, context)
        msg_box("Renamed {} objects".format(n))

        return{"FINISHED"}


class SelectByName(bpy.types.Operator):
    bl_idname = "helpers.select_by_name"
    bl_label = "Select by name"
    bl_description = (
        "Selects all objects that contain the name"
        )

    def execute(self, context):
        n = tools.select_by_name(self, context)
        msg_box("Selected {} objects".format(n))
        return{"FINISHED"}


class SelectByData(bpy.types.Operator):
    bl_idname = "helpers.select_by_data"
    bl_label = "Select by data"
    bl_description = (
        "Selects all objects with the same object data (mesh)"
    )

    def execute(self, context):
        n = tools.select_by_data(self, context)
        msg_box("Selected {} objects".format(n))
        return{"FINISHED"}


class SetInstanceProperty(bpy.types.Operator):
    bl_idname = "helpers.set_instance_property"
    bl_label = "Mark as Instance"
    bl_description = (
        "Marks all selected objects as instances"
    )

    def execute(self, context):
        n = tools.set_property_to_selected(self, context, "is_instance", True)
        msg_box("Marked {} objects as instances".format(n))
        return{"FINISHED"}


class RemoveInstanceProperty(bpy.types.Operator):
    bl_idname = "helpers.rem_instance_property"
    bl_label = "Remove Instance property"
    bl_description = (
        ""
    )

    def execute(self, context):
        n = tools.set_property_to_selected(self, context, "is_instance", False)
        msg_box("Marked {} objects as instances".format(n))
        return{"FINISHED"}


class BatchBake(bpy.types.Operator):
    bl_idname = "helpers.batch_bake_model"
    bl_label = "Bake all selected"
    bl_description = (
        "Bakes the light cast by lamps in the current scene to the Instance"
        "model colors"
    )

    def execute(self, context):
        n = tools.batch_bake(self, context)
        msg_box("Baked {} objects".format(n))
        return{"FINISHED"}


class LaunchRV(bpy.types.Operator):
    bl_idname = "helpers.launch_rv"
    bl_label = "Launch RVGL"
    bl_description = (
        "Launches the game"
    )

    def execute(self, context):
        rvgl_dir = context.scene.revolt.revolt_dir
        if "rvgl.exe" in os.listdir(rvgl_dir):
            executable = "rvgl.exe"
        elif "rvgl" in os.listdir(rvgl_dir):
            executable = "rvgl"
        else:
            return{"FINISHED"}
        subprocess.Popen(["{}/{}".format(rvgl_dir, executable), "-window", "-nointro", "-sload", "-dev"])
        return{"FINISHED"}