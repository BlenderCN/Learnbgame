import bpy

class Speech2AnimTrainingVideosItems(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row()
        row.prop(item, "name", text="", emboss=False, translate=False, icon='RENDER_ANIMATION')

    def invoke(self, context, event):
        pass  

class Speech2AnimTrainingPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_speech_2_anim_training"
    bl_label = "Speech2Anim Training"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        scn = context.scene

        #input paths
        row = layout.row()
        row.prop(scn.speech2anim_data, "training_model_path")
        row = layout.row()
        row.prop(scn.speech2anim_data, "training_videos_path")
        #Config file
        row = layout.row()
        row.label("Configuration")
        row = layout.row()
        row.prop(scn.speech2anim_data, "config_type", expand=True)
        if scn.speech2anim_data.config_type == 'EXTERNAL':
            row = layout.row()
            row.prop(scn.speech2anim_data, "external_config_path")

            row = layout.row(align=True)
            row.operator("s2a.create_config")
            open_btn = row.operator("s2a.open_file")
            open_btn.path = scn.speech2anim_data.external_config_path

        row = layout.row()
        row.label("Training")
        #### video list
        if scn.speech2anim_data.training_videos_list:
            row = layout.row()
            row.template_list("Speech2AnimTrainingVideosItems", "", 
                scn.speech2anim_data, "training_videos_list", 
                scn.speech2anim_data, "selected_training_video_index", rows=2)

            col = row.column(align=True)
            col.operator("s2a.training_videos_list_actions", icon='POSE_DATA', text="").action = 'CLEAR_POSE'
            col.operator("s2a.training_videos_list_actions", icon='MUTE_IPO_ON', text="").action = 'CLEAR_AUDIO'
            col.operator("s2a.training_videos_list_actions", icon='RESTRICT_VIEW_OFF', text="").action = 'SEE_INFO'
            col.operator("s2a.save_label_modifications", icon='SAVE_COPY', text="")
        #### video list
        row = layout.row()
        row.scale_y = 1.5
        row.operator("s2a.train_model")
        row = layout.row()
        row.operator("s2a.train_model_mods")
        row = layout.row()
        row.operator("s2a.open_training_log")
        row = layout.row()
        row.scale_y = 1.5
        #Cleaning buttons
        row = layout.row()
        row.label("Cleaning")
        row = layout.row(align=True)
        row.operator("s2a.clear_training_generated_files")
        row.operator("s2a.clear_animation")
        row.operator("s2a.reset_state")


class Speech2AnimAnimatePanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_speech_2_anim_animate"
    bl_label = "Speech2Anim Animation"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        row = layout.row()
        row.prop(scn.speech2anim_data, "animate_model_path")
        row = layout.row()
        row.prop(scn.speech2anim_data, "input_file")
        row = layout.row()
        row.label("Configuration")
        row = layout.row()
        row.prop(scn.speech2anim_data, "animation_config_type", expand=True)
        if scn.speech2anim_data.animation_config_type == 'EXTERNAL':
            row = layout.row()
            row.prop(scn.speech2anim_data, "external_animation_config_path")

            row = layout.row(align=True)
            row.operator("s2a.create_animation_config")
            open_btn = row.operator("s2a.open_file")
            open_btn.path = scn.speech2anim_data.external_animation_config_path

        row = layout.row()
        row.label("Animation")
        row = layout.row()
        row.scale_y = 1.5
        row.operator("s2a.animate")
        row = layout.row()
        row.label("Cleaning")
        row = layout.row()
        op = row.operator("s2a.clear_animation")


def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)
