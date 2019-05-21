import bpy

bl_info = {
    "name":        "Cinebars",
    "description": "Add fake-letterboxing without changing the resolution of your video.",
    "author":      "ZoomTen",
    "version":     (0, 0, 2),
    "blender":     (2, 71, 0),
    "wiki_url":    "https://github.com/ZoomTen/blender-vse-cinebars",
    "tracker_url": "https://github.com/ZoomTen/blender-vse-cinebars/issues",
    "location":    "Video Sequence Editor > Properties > Cinebars",
    "category":    "Sequencer"
    }

# vars
class cbVals(bpy.types.PropertyGroup):
    ratio_x = bpy.props.FloatProperty(
                name="ratio_x",
                description="Horizontal ratio",
                default=16.0
             )
    ratio_y = bpy.props.FloatProperty(
                name="ratio_y",
                description="Vertical ratio",
                default=9.0
             )

# funcs
def msgbox(message = "", title = "info", icon = 'INFO'):
    def draw(self, context):
        self.layout.label(message)
    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

def main(context):
    # get render resolution
    rsx = bpy.context.scene.render.resolution_x
    rsy = bpy.context.scene.render.resolution_y
    
    # get target AR
    target_rsx = context.scene.cb_ratios.ratio_x
    target_rsy = context.scene.cb_ratios.ratio_y
    
    if target_rsx/target_rsy == rsx/rsy:
        msgbox("Source AR is the same as destination AR!")
        return 0
    
    
    bpy.ops.sequencer.effect_strip_add(frame_start=bpy.context.scene.frame_start,
                                       frame_end=bpy.context.scene.frame_end,
                                       type="COLOR")
    color = context.scene.sequence_editor.active_strip
    
    bpy.ops.sequencer.effect_strip_add(type="TRANSFORM")
    bar = context.scene.sequence_editor.active_strip
    
    bar.name = "cinebars "+str('%.2f' % target_rsx)+":"+str('%.2f' % target_rsy)
    # wide ratio
    if target_rsx/target_rsy > rsx/rsy:
        bar.scale_start_y = (1-((rsx/target_rsx*target_rsy)/rsy))/2
        bar.translate_start_y= 50 - (bar.scale_start_y*50)
        bar.blend_type='ALPHA_OVER'
        bpy.ops.sequencer.duplicate_move(
                                            SEQUENCER_OT_duplicate={"mode":'TRANSLATION'},
                                            TRANSFORM_OT_seq_slide={"value":(2,1)}
                                        )
        otherbar = context.scene.sequence_editor.active_strip
        otherbar.use_flip_y = True
        otherbar.blend_type='ALPHA_OVER'
        color.mute = True
        # i would make them into a metastrip but there isn't a function for
        # that apparently
    # tall / square ratio
    if target_rsx/target_rsy < rsx/rsy:
        bar.scale_start_x = (1-((rsy/target_rsy*target_rsx)/rsx))/2
        bar.translate_start_x= 50 - (bar.scale_start_x*50)
        bar.blend_type='ALPHA_OVER'
        bpy.ops.sequencer.duplicate_move(
                                            SEQUENCER_OT_duplicate={"mode":'TRANSLATION'},
                                            TRANSFORM_OT_seq_slide={"value":(2,1)}
                                        )
        otherbar = context.scene.sequence_editor.active_strip
        otherbar.use_flip_x = True
        otherbar.blend_type='ALPHA_OVER'
        color.mute = True
        # i would make them into a metastrip but there isn't a function for
        # that which doesn't require selections apparently

# actions
class cbMake(bpy.types.Operator):
    bl_idname = "sequencer.cb_make"
    bl_label = "Make Cinebars"

    def execute(self, context):
        main(context)
        return {'FINISHED'}
    
# ui
class cbPanel(bpy.types.Panel):
    bl_space_type = "SEQUENCE_EDITOR"
    bl_region_type = "UI"
    bl_label = "Cinebars"
    bl_idname = "sequencer.cb_panel"
    def draw(self, context):
        l = self.layout
        l.prop(context.scene.cb_ratios, "ratio_x",text="Horizontal ratio")
        l.prop(context.scene.cb_ratios, "ratio_y",text="Vertical ratio")
        l.operator('sequencer.cb_make',
                    text='Generate Cinebars Strips',
                    icon='FILE_TICK')

# addon registry
def register():
    bpy.utils.register_class(cbVals)
    bpy.utils.register_class(cbMake)
    bpy.utils.register_class(cbPanel)
    bpy.types.Scene.cb_ratios = bpy.props.PointerProperty(type=cbVals)

def unregister():
    del bpy.types.Scene.cb_ratios
    bpy.utils.unregister_class(cbMake)
    bpy.utils.unregister_class(cbPanel)
    bpy.utils.unregister_class(cbVals)

if __name__ == "__main__":
    register()
