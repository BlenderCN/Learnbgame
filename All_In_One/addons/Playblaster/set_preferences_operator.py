import bpy

class PlayblasterSetPreferences(bpy.types.Operator):
    """Set Playblaster scene settings"""
    bl_idname = "playblaster.set_preferences"
    bl_label = "Playblaster Settings"

    # UI props
    show_debug = bpy.props.BoolProperty()
    show_general = bpy.props.BoolProperty()
    show_frame_range = bpy.props.BoolProperty()
    show_engine = bpy.props.BoolProperty()
    show_simplify = bpy.props.BoolProperty()

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        scn = context.scene
        layout = self.layout

        # debug
        box = layout.box()
        row = box.row(align = True)
        icon_debug = 'TRIA_DOWN' if self.show_debug else 'TRIA_RIGHT'
        row.prop(self, 'show_debug', text = '', icon = icon_debug, emboss = False)
        row.label(text = 'Debug')
        row.prop(scn, 'playblaster_debug', text = '')
        if self.show_debug :
            row = box.row()
            if not scn.playblaster_debug :
                row.enabled = False
            row.prop(scn, 'playblaster_is_rendering')


        # general settings
        box = layout.box()
        row = box.row(align = True)
        icon_general = 'TRIA_DOWN' if self.show_general else 'TRIA_RIGHT'
        row.prop(self, 'show_general', text = '', icon = icon_general, emboss = False)
        row.label(text = 'General Settings')

        if self.show_general :

            # resolution percentage
            box.prop(scn, 'playblaster_resolution_percentage', slider = True)

            # Compositing
            box.prop(scn, 'playblaster_use_compositing')

            # Frame range override
            subbox = box.box()
            row = subbox.row(align = True)
            icon_frame_range = 'TRIA_DOWN' if self.show_frame_range else 'TRIA_RIGHT'
            row.prop(self, 'show_frame_range', text = '', icon = icon_frame_range, emboss = False)
            row.label(text = "Frame Range")
            row.prop(scn, 'playblaster_frame_range_override', text = '')
            if self.show_frame_range :
                col = subbox.column(align = True)
                if not scn.playblaster_frame_range_override :
                    col.enabled = False
                col.prop(scn, 'playblaster_frame_range_in')
                col.prop(scn, 'playblaster_frame_range_out')

            # Simplify
            subbox = box.box()
            row = subbox.row(align = True)
            icon_simplify = 'TRIA_DOWN' if self.show_simplify else 'TRIA_RIGHT'
            row.prop(self, 'show_simplify', text = '', icon = icon_simplify, emboss = False)
            row.label(text = 'Simplify')
            row.prop(scn, 'playblaster_simplify', text = '')
            if self.show_simplify :
                col = subbox.column(align = True)
                if not scn.playblaster_simplify :
                    col.enabled = False
                col.prop(scn, 'playblaster_simplify_subdivision')
                col.prop(scn, 'playblaster_simplify_particles')


        # render engine
        box = layout.box()
        row = box.row(align = True)
        icon_engine = 'TRIA_DOWN' if self.show_engine else 'TRIA_RIGHT'
        row.prop(self, 'show_engine', text = '', icon = icon_engine, emboss = False)
        row.label(text = "Engine")
        row.prop(scn, 'playblaster_render_engine', text = "")

        if self.show_engine :

            # EEVEE
            if scn.playblaster_render_engine == "BLENDER_EEVEE" :
                # eevee settings
                box.prop(scn, 'playblaster_eevee_samples')
                box.prop(scn, 'playblaster_eevee_dof')
                # shadow cube size
                # shadow cascade size
                # AO
                # Motion blur
                # volumetric
                # overscan

            # workbench
            elif scn.playblaster_render_engine == "BLENDER_WORKBENCH" :
                pass
                # lighting type
                # color type
                # backface
                # xray
                # shadow
                # cavity
                # dof
                # outline
                # specular

        layout.separator()

        layout.operator("playblaster.render", icon = 'RENDER_ANIMATION')
        #layout.prop(context.scene, "playblaster_previous_render")
        layout.operator("playblaster.play_rendered", icon = 'PLAY')
