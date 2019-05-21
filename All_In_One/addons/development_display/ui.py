import bpy
from bpy.types import Panel, PropertyGroup
from bpy.props import BoolProperty, FloatVectorProperty, StringProperty, FloatProperty, IntVectorProperty
from .plot_ui_functions import valid_expression, eval_expression


class DisplaySettings(PropertyGroup):
    enabled = BoolProperty(
        name='enabled',
        default=True)
    show_gl = BoolProperty(
        name='Display GL',
        default=True)
    show_gl_points = BoolProperty(
        name='Points GL',
        default=True)
    show_gl_edges = BoolProperty(
        name='Edges GL',
        default=True)
    show_gl_point_chains = BoolProperty(
        name='Pointchains GL',
        default=True)
    show_gl_plots = BoolProperty(
        name='Plots',
        default=True)
    show_gl_mats = BoolProperty(
        name='Matrizies GL',
        default=True)
    show_gl_eulers = BoolProperty(
        name='Eulers GL',
        default=True)
    show_gl_quats = BoolProperty(
        name='Quaternions GL',
        default=True)
    show_gl_bm = BoolProperty(
        name='Bmesh GL',
        default=True)
    show_gl_bm_faces = BoolProperty(
        name='Bmesh GL Faces',
        default=True)

    show_text = BoolProperty(
        name='Display Names',
        default=True)
    show_text_points = BoolProperty(
        name='Point Names',
        default=True)
    show_text_edges = BoolProperty(
        name='Edge Names',
        default=True)
    show_text_point_chains = BoolProperty(
        name='Pointchain Names',
        default=True)
    show_text_plots = BoolProperty(
        name='Plot Names',
        default=True)
    show_text_mats = BoolProperty(
        name='Matrizies Names',
        default=True)
    show_text_eulers = BoolProperty(
        name='Eulers Names',
        default=True)
    show_text_quats = BoolProperty(
        name='Quaternions Names',
        default=True)
    show_text_bm = BoolProperty(
        name='Bmesh Names',
        default=True)
    show_text_bm_verts = BoolProperty(
        name='Bmesh Names',
        default=True)
    show_text_bm_edges = BoolProperty(
        name='Bmesh Names',
        default=True)
    show_text_bm_faces = BoolProperty(
        name='Bmesh Names',
        default=True)

    color_points = FloatVectorProperty(
        name='Points',
        subtype='COLOR',
        size=4,
        default=(1,0,0,1),
        min=0, max=1)
    color_edges = FloatVectorProperty(
        name='Edges',
        subtype='COLOR',
        size=4,
        default=(0,1,0,1),
        min=0, max=1)
    color_point_chains = FloatVectorProperty(
        name='Pointchains',
        subtype='COLOR',
        size=4,
        default=(0.5, 1, 1, 1),
        min=0, max=1)
    color_faces = FloatVectorProperty(
        name='Faces',
        subtype='COLOR',
        size=4,
        default=(1, 1, 1, 0.4),
        min=0, max=1)
    color_text = FloatVectorProperty(
        name='Text',
        subtype='COLOR',
        size=4,
        default=(1,1,1,1),
        min=0, max=1)

    plot_scale = FloatVectorProperty(
        name='Plot Scale',
        subtype='XYZ',
        size=2,
        min=0,soft_min=0,
        default=(1, 1))
    plot_co = IntVectorProperty(
        name='Plot Center',
        subtype='XYZ',
        size=2,
        min=0,soft_min=0,
        default=(750, 200))
    plot_ui = StringProperty(
        name='Plotting Function',
        default='',
        description='namespace imports: * from math and numpy as np.\n'
            'To update hit Clear Plots.\n'
            'use "x" in the expression for the interval input below.'
        )
    plot_ui_interval = FloatVectorProperty(
        name='Interval',
        default=(0,1,0.1),
        description='X-Axis Range for the expression.\n'
            '[from, to, stepsize]\n'
            'use "x" as varaible in the expression'
        )



class DisplayUI(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Devel Display"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        settings = context.window_manager.display_settings
        display = bpy.types.WindowManager.display

        col = layout.column(align=True)
        col.operator('scene.display_clear')
        
        col.prop(settings, 'enabled')
        if not settings.enabled and display.draw_handle:
            display.draw_stop()
        elif settings.enabled and not display.draw_handle:
            display.draw_start()

        box = layout.box()
        split = box.split()

        #GL DISPLAY
        col = split.column(align=True)
        
        col.prop(settings, 'show_gl', text='GL')
        col.active = settings.show_gl
        col.prop(settings, 'show_gl_points',toggle=True)
        col.prop(settings, 'show_gl_edges',toggle=True)
        col.prop(settings, 'show_gl_point_chains',toggle=True)
        col.prop(settings, 'show_gl_mats',toggle=True)
        col.prop(settings, 'show_gl_eulers',toggle=True)
        col.prop(settings, 'show_gl_quats',toggle=True)
        row = col.row(align=True)
        row.prop(settings, 'show_gl_bm',toggle=True)
        row.prop(settings, 'show_gl_bm_faces',toggle=True, text='Faces')

        #TEXT DISPLAY
        col = split.column(align=True)
        
        col.prop(settings, 'show_text', text='Names')
        col.active = settings.show_text
        col.prop(settings, 'show_text_points',toggle=True)
        col.prop(settings, 'show_text_edges',toggle=True)
        col.prop(settings, 'show_text_point_chains',toggle=True)
        col.prop(settings, 'show_text_mats',toggle=True)
        col.prop(settings, 'show_text_eulers',toggle=True)
        col.prop(settings, 'show_text_quats',toggle=True)
        row = col.row(align=True)
        #row.prop(settings, 'show_text_bm',toggle=True)
        row.prop(settings, 'show_text_bm_verts',toggle=True, text='Vert')
        row.prop(settings, 'show_text_bm_edges',toggle=True, text='Edge')
        row.prop(settings, 'show_text_bm_faces',toggle=True, text='Face')

        #GL COLORS
        col = box.column(align=True)
        col.active = settings.show_gl
        col.separator()
        row = col.row()
        row.prop(settings, 'color_text')
        row = col.row()
        row.prop(settings, 'color_points')
        row = col.row()
        row.prop(settings, 'color_edges')
        row = col.row()
        row.prop(settings, 'color_point_chains')
        row = col.row()
        row.prop(settings, 'color_faces')

        #PLOTS
        box = layout.box()
        col = box.column()
        col.separator()
        col.prop(settings, 'show_gl_plots', text='Show Plots', toggle=True)

        if settings.show_gl_plots:
            if display.plots:
                col.operator('scene.display_clear_plots')

            #ui plotting
            col.prop(settings, 'plot_ui', text='')
            row = col.row()
            row.prop(settings, 'plot_ui_interval', text='')

            if valid_expression(settings.plot_ui):
                name = 'UI Plot: ' + settings.plot_ui
                if not name in display.plots:
                    display.add_plot(*eval_expression(settings.plot_ui), k=name)
            
            #plot ui transform
            col.prop(settings, 'plot_co')
            col.prop(settings, 'plot_scale')

        #INFO
        col = layout.column()
        for line in str(display).split('\n'):
            col.label(line)

