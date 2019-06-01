import bpy
from .face_material_id import save_material_names_and_indices_to_file, \
    load_material_names_and_indices_from_file, apply_material_indices_and_names, dump_material_indices_and_names, \
    check_material_infos_on_mesh


class FaceMaterialIdPanel(bpy.types.Panel):
    bl_label = "Face Material Id"
    bl_idname = "face_material_id_panel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"

    def draw(self, context):
        layout = self.layout
        layout.operator("cube.save_face_material_id_operator", icon='EXPORT')
        layout.operator("cube.load_face_material_id_operator", icon='IMPORT')


class SaveFaceMaterialIdOperator(bpy.types.Operator):
    bl_idname = "cube.save_face_material_id_operator"
    bl_label = "Save Face Material Id"
    bl_description = "Save face material id to file"

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        dump = dump_material_indices_and_names(context.object)
        save_material_names_and_indices_to_file(dump, self.filepath + (".json" if not self.filepath.endswith(".json") else ""))
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class LoadFaceMaterialIdOperator(bpy.types.Operator):
    bl_idname = "cube.load_face_material_id_operator"
    bl_label = "Load Face Material Id"
    bl_description = "Load Face Material Id from file"
    bl_options = {'REGISTER', 'UNDO'}

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        # switch to object mode to ensure geometry is properly updated
        previous_mode = context.object.mode
        bpy.ops.object.mode_set(mode="OBJECT")
        # load, check and apply material data on object
        info = load_material_names_and_indices_from_file(self.filepath)
        ok, message = check_material_infos_on_mesh(info, context.object)
        if ok:
            apply_material_indices_and_names(context.object, info)
        # switch back to previous mode
        bpy.ops.object.mode_set(mode=previous_mode)
        # draw function for popup message

        def draw(self, context):
            self.layout.label(message)

        if not ok:
            context.window_manager.popup_menu(draw, title="Warning", icon="ERROR")
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
