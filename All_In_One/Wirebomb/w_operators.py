import bpy
import time
from .w_b_scene import BlenderSceneW
from . import w_var


class WireframeOperator(bpy.types.Operator):
    """Set up wireframe/clay render"""
    bl_label = "Set up new"
    bl_idname = 'scene.wirebomb_set_up_new'

    def execute(self, context):
        start = time.time()
        original_scene = context.scene
        original_scene_inst = BlenderSceneW(original_scene, False)

        # saves information from UI and (re)sets variables
        original_scene_inst.wirebomb_set_variables()

        # checks for any errors
        success, error_msg = original_scene_inst.wirebomb_error_check()

        if success:

            # initiates progress bar and updates it to 1 %
            context.window_manager.progress_begin(0, 100)
            context.window_manager.progress_update(1)

            # creates wireframe/clay scene object
            scene_inst = BlenderSceneW(original_scene, w_var.cb_backup, w_var.scene_name_1)
            scene_inst.prepare_fast_setup()

            # sets all used objects to three sets: affected objects, other object and all used objects
            # (need to do after I copy the scene to get the objects from the copied scene)
            scene_inst.add_objects_used()
            
            scene_inst.get_scene().wirebomb.data_renderengine = scene_inst.get_renderengine()

            # updates progress bar to 25 %
            bpy.context.window_manager.progress_update(25)

            if not w_var.cb_clay_only:

                # runs wireframing (w/ clay)
                if w_var.wireframe_method == 'WIREFRAME_FREESTYLE':
                    scene_inst.set_up_wireframe_freestyle()

                elif w_var.wireframe_method == 'WIREFRAME_MODIFIER':
                    scene_inst.set_up_wireframe_modifier()

            else:

                # only sets up clay
                scene_inst.set_up_clay_only()

            scene_inst.prepare_fast_setup(revert=True)

            # terminates the progress bar
            context.window_manager.progress_end()

            self.report({'INFO'}, "Setup done in {} seconds!".format(round(time.time() - start, 3)))

        elif not success:
            self.report({'ERROR'}, error_msg)

        return {'FINISHED'}


class ConfigSaveOperator(bpy.types.Operator):
    """Saves a config INI file"""
    bl_label = "Save"
    bl_idname = 'scene.wirebomb_config_save'

    filepath = bpy.props.StringProperty()
    filename = bpy.props.StringProperty()

    def execute(self, context):
        if self.filename.lower().endswith('.ini'):
            scene_inst = BlenderSceneW(context.scene, False)
            scene_inst.wirebomb_config_save(self.filepath)
            self.report({'INFO'}, "{} saved successfully!".format(self.filename))

        else:
            self.report({'ERROR'}, "File extension must be INI !")

        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class ConfigLoadOperator(bpy.types.Operator):
    """Loads a config INI file"""
    bl_label = "Load"
    bl_idname = 'scene.wirebomb_config_load'

    filepath = bpy.props.StringProperty()
    filename = bpy.props.StringProperty()

    def execute(self, context):
        if self.filename.lower().endswith('.ini'):
            try:
                scene_inst = BlenderSceneW(context.scene, False)
                scene_inst.wirebomb_config_load(self.filepath)
                self.report({'INFO'}, "{} loaded successfully!".format(self.filename))

            except KeyError as e:
                self.report({'ERROR'}, "Key missing in file: {}.".format(e))

        else:
            self.report({'ERROR'}, "File extension must be INI !")

        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class SelectLayersAffectedOperator(bpy.types.Operator):
    """Selects all 'Affected' layers"""
    bl_label = "All"
    bl_idname = 'scene.wirebomb_select_layers_affected'

    def execute(self, context):
        for i in range(0, 20):
            context.scene.wirebomb.layers_affected[i] = True

        return {'FINISHED'}


class SelectLayersOtherOperator(bpy.types.Operator):
    """Selects all 'Other included' layers"""
    bl_label = "All"
    bl_idname = 'scene.wirebomb_select_layers_other'

    def execute(self, context):
        for i in range(0, 20):
            context.scene.wirebomb.layers_other[i] = True

        return {'FINISHED'}


class DeselectLayersAffectedOperator(bpy.types.Operator):
    """Deselects all 'Affected' layers"""
    bl_label = "None"
    bl_idname = 'scene.wirebomb_deselect_layers_affected'

    def execute(self, context):
        for i in range(0, 20):
            context.scene.wirebomb.layers_affected[i] = False

        return {'FINISHED'}


class DeselectLayersOtherOperator(bpy.types.Operator):
    """Deselects all 'Other included' layers"""
    bl_label = "None"
    bl_idname = 'scene.wirebomb_deselect_layers_other'

    def execute(self, context):
        for i in range(0, 20):
            context.scene.wirebomb.layers_other[i] = False

        return {'FINISHED'}
