import bpy

b_version = 256
if hasattr(bpy.utils, 'register_class'):
    b_version = 257

class B2RexGameMenu(bpy.types.Menu):
    bl_label = "Game"

    def draw(self, context):
        layout = self.layout

        gs = context.scene.game_settings

        layout.operator("b2rex.game_start")
        #layout.operator("view3d.game_start")

        layout.separator()

        layout.prop(gs, "show_debug_properties")
        layout.prop(gs, "show_framerate_profile")
        layout.prop(gs, "show_physics_visualization")
        layout.prop(gs, "use_deprecation_warnings")
        layout.prop(gs, "use_animation_record")
        layout.separator()
        layout.prop(gs, "use_auto_start")


class Menu(bpy.types.Header):
    bl_label = 'sim'
    bl_space_type = 'INFO'
    def draw(self, context):
        session = bpy.b2rex_session
        props = context.scene.b2rex_props
        self.default_menu(context, session, props)
        self.draw_connections(context, self.layout, session, props)

    def draw_callback(self, referer, context):
        #print("redraw menu")
        bpy.ops.b2rex.processqueue()
        if bpy.b2rex_session.stats[5]:
            context.screen.name = context.screen.name
        
    def draw_connections(self, context, layout, session, props):
        if len(props.connection.list):
            if props.connection.search and props.connection.search in props.connection.list:
                if session.simrt:
                    if session.simrt.connected:
                        layout.operator("b2rex.toggle_rt", text="RT",
                                        icon='PMARKER_ACT')
                    else:
                        layout.operator("b2rex.toggle_rt", text="RT",
                                        icon='PMARKER_SEL')
                else:
                    layout.prop_search(props.connection, 'search', props.connection,
                        'list', icon='PMARKER_SEL',text='')
                    layout.operator("b2rex.toggle_rt", text="RT", icon='PMARKER')
                if session.simrt:
                    session.processView()
                    if b_version == 256:
                        bpy.ops.b2rex.processqueue()
                    else:
                        if not hasattr(session, "_redraw_handle"):
                            session._redraw_handle =  context.region.callback_add(self.draw_callback, (self,
                                                                         context),
                                                    'POST_PIXEL')
                        for area in context.screen.areas:
                            if area.type in ['INFO', 'VIEW_3D']:
                                area.tag_redraw()

        if session.stats[5] > 10:
            layout.label(text='',icon='PREVIEW_RANGE')
            #layout.label('',text="q: "+str(session.stats[5]))


    def default_menu(self, context, session, props):
        wm = context.window_manager
        window = context.window
        scene = context.scene
        screen = context.screen
        rd = scene.render
        layout = self.layout

        row = layout.row(align=True)

        sub = row.row(align=True)
        sub.menu("INFO_MT_file")
        sub.menu("INFO_MT_add")
        if rd.use_game_engine: sub.menu("B2RexGameMenu")
        else: sub.menu("INFO_MT_render")
        layout.separator()
        sub.menu("INFO_MT_instances")
        sub.menu("INFO_MT_groups")

        #layout.separator()
        layout.operator("wm.window_fullscreen_toggle", icon='FULLSCREEN_ENTER', text="")


        layout.template_header()
        if not context.area.show_menus:
            if window.screen.show_fullscreen: layout.operator("screen.back_to_previous", icon='SCREEN_BACK', text="Back to Previous")
            else: layout.template_ID(context.window, "screen", new="screen.new", unlink="screen.delete")
            layout.template_ID(context.screen, "scene", new="scene.new", unlink="scene.delete")

            layout.separator()
            layout.template_running_jobs()
            layout.template_reports_banner()
            layout.separator()
            if rd.has_multiple_engines: layout.prop(rd, "engine", text="")

            layout.label(text=scene.statistics())
            layout.menu( "INFO_MT_help" )

        else:
            row = layout.row(align=True)        # align makes buttons compact together
            #row.operator("screen.frame_jump", text="", icon='REW').end = False
            row.operator("screen.keyframe_jump", text="", icon='PREV_KEYFRAME').next = False
            if not screen.is_animation_playing: row.operator("screen.animation_play", text="", icon='PLAY')
            else: sub = row.row(); sub.scale_x = 1.0; sub.operator("screen.animation_play", text="", icon='PAUSE')
            row.operator("screen.keyframe_jump", text="", icon='NEXT_KEYFRAME').next = True
            #row.operator("screen.frame_jump", text="", icon='FF').end = True
            row = layout.row(align=True)
            layout.prop(scene, "frame_current", text="")

        #if not context.area.show_menus:

