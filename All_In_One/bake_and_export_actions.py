bl_info = {
    "name": "Bake And Export All Actions",
    "author": "Olli Hihnala",
    "version": (0, 1),
    "blender": (2, 79, 0),
    "location": "View3D > Object > Bake And Export All Actions",
    "description": "Bake all actions from control to deform rig and export them",
    "warning": "",
    "wiki_url": "",
    "category": "Learnbgame",
}

from math import pi
import bpy
from bpy.types import Operator, AddonPreferences
from bpy.props import StringProperty
from os import path


def main(self, context):
    target = None
    source = None
    prefix = context.user_preferences.addons[__name__].preferences.source_prefix
    newPrefix = context.user_preferences.addons[__name__].preferences.target_prefix
    exportActions = []
    exportObjects = []

    save_location = bpy.path.abspath(context.user_preferences.addons[__name__].preferences.filepath)
    if not path.exists(save_location):
            self.report({'INFO'}, "Invalid path update in addon preferences")
            return {'CANCELLED'}


    if len(context.selected_objects) >= 2:
        if bpy.context.object.type == 'ARMATURE':
            target = bpy.context.object
            target.select = False
        else:
            self.report({'INFO'}, "Active object not of type ARMATURE")
            return {'CANCELLED'}

        checkType = [
            object.type for object in context.selected_objects if object.type == 'ARMATURE']
        if len(checkType) != 1:
            self.report({'INFO'}, "Source ARMATURE not found")
            return {'CANCELLED'}

        for object in context.selected_objects:
            if object.type == 'ARMATURE':
                source = object
                continue
            exportObjects.append(object)
            object.select = False

    else:
        self.report({'INFO'}, "Select at least two objects")
        return {'CANCELLED'}

    save_location = path.join(save_location,target.name+".fbx")

    target.select = True
    for object in context.selected_objects:
        bpy.context.scene.objects.active = object
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.pose.loc_clear()
        bpy.ops.pose.rot_clear()
        bpy.ops.pose.scale_clear()
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    bpy.context.scene.objects.active = target

    for action in bpy.data.actions:
        if action.name.startswith(prefix):
            bpy.context.scene.update()
            source.animation_data.action = bpy.data.actions.get(action.name)
            print(action.name)
            bpy.context.scene.update()
            actionRange = bpy.data.actions[action.name].frame_range
            print(actionRange)
            actionName = action.name.replace(prefix, newPrefix, 1)
            exportAction = bpy.data.actions.new(name=actionName)
            exportActions.append(exportAction)
            target.animation_data_create()
            target.animation_data.action = bpy.data.actions.get(actionName)
            bpy.ops.nla.bake(frame_start=actionRange[0], frame_end=actionRange[1], step=1, only_selected=False,
                             visual_keying=True, clear_constraints=False, clear_parents=False, use_current_action=True, bake_types={'POSE'})
            bpy.context.scene.update()

    source.select = False

    bpy.ops.object.mode_set(mode='POSE', toggle=False)
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.pose.loc_clear()
    bpy.ops.pose.rot_clear()
    bpy.ops.pose.scale_clear()
    bpy.ops.pose.constraints_clear()
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)

    for action in bpy.data.actions:
        if action not in exportActions:
            bpy.data.actions.remove(action)

    for object in exportObjects:
        object.select = True

    bpy.ops.export_scene.fbx(filepath=save_location, check_existing=False, axis_forward='-Z', axis_up='Y', filter_glob="*.fbx", version='BIN7400', ui_tab='MAIN', use_selection=True, global_scale=1.0, apply_unit_scale=True, apply_scale_options='FBX_SCALE_UNITS', bake_space_transform=False, object_types={
                             'ARMATURE', 'MESH'}, use_mesh_modifiers=True, use_mesh_modifiers_render=True, mesh_smooth_type='OFF', use_mesh_edges=False, use_tspace=False, use_custom_props=False, add_leaf_bones=True, primary_bone_axis='Y', secondary_bone_axis='X', use_armature_deform_only=False, armature_nodetype='NULL', bake_anim=True, bake_anim_use_all_bones=True, bake_anim_use_nla_strips=True, bake_anim_use_all_actions=True, bake_anim_force_startend_keying=True, bake_anim_step=1.0, bake_anim_simplify_factor=1.0, use_anim=True, use_anim_action_all=True, use_default_take=False, use_anim_optimize=True, anim_optimize_precision=6.0, path_mode='AUTO', embed_textures=False, batch_mode='OFF', use_batch_own_dir=True, use_metadata=True)

    target.select = False

    source.select = True
    bpy.context.scene.objects.active = source
    bpy.ops.object.mode_set(mode='POSE', toggle=False)
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.pose.loc_clear()
    bpy.ops.pose.rot_clear()
    bpy.ops.pose.scale_clear()
    bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
    source.select = False

    return {'FINISHED'}


class BakeAndExportActions(bpy.types.Operator):
    """Bake all actions from source to target and export them"""
    bl_idname = "object.bake_and_export_actions"
    bl_label = "Bake And Export Actions"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__name__].preferences

        info = ("Path: %s, Source Prefix: %s, Target Prefix %s" %
                (addon_prefs.filepath, addon_prefs.source_prefix, addon_prefs.target_prefix))

        self.report({'INFO'}, info)
        result = main(self, context)
        if 'CANCELLED' in result:
            return {'CANCELLED'}
        else:
            bpy.ops.ed.undo()
            return {'FINISHED'}


class BakeAndExportActionsPrefs(AddonPreferences):
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __name__

    filepath = StringProperty(
        name="Export Folder",
        subtype='FILE_PATH',
    )
    source_prefix = StringProperty(
        name="Source Action Name Prefix",
        default='Ctrl_',
    )
    target_prefix = StringProperty(
        name="Export Action Name Prefix",
        default='Anim_',
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text="Preferences")
        layout.prop(self, "filepath")
        layout.prop(self, "source_prefix")
        layout.prop(self, "target_prefix")


def add_to_object_menu(self, context):
    self.layout.operator(BakeAndExportActions.bl_idname)


def register():
    bpy.utils.register_class(BakeAndExportActions)
    bpy.utils.register_class(BakeAndExportActionsPrefs)
    bpy.types.VIEW3D_MT_object.append(add_to_object_menu)


def unregister():
    bpy.utils.unregister_class(BakeAndExportActions)
    bpy.utils.register_class(BakeAndExportActionsPrefs)
    bpy.types.VIEW3D_MT_object.remove(add_to_object_menu)


if __name__ == "__main__":
    register()
